import datetime
import logging
import secrets
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import models
from database import get_db
from game_engine import GameEngine
from round_bonuses import *
import json
import copy
import uuid
import asyncio
import os
import stat
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

app = FastAPI()
ENV = os.environ.get("ENV", "development")

class UsernameUpdate(BaseModel):
    username: str

if ENV == "production":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    static_directory = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_directory), name="static")

    app.add_middleware(SessionMiddleware, secret_key="!secret")
    
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError(
            "Missing Google OAuth credentials. "
            "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables"
        )

    oauth = OAuth()
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        client_kwargs={'scope': 'openid email profile'},
    )

    connections_in_the_lobby: List[Dict] = []
    connections_to_games: List[Dict] = []
    game_engines = {}

else:
    connected_clients: List[Dict] = []
    current_players = []
    game_engine = None

if ENV == "production":
    @app.get('/login')
    async def login(request: Request):
        # Generate and store a nonce in the session
        nonce = secrets.token_urlsafe(16)
        request.session['nonce'] = nonce
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri, nonce=nonce)

    @app.get('/auth')
    async def auth(request: Request, db: Session = Depends(get_db)):
        try:
            token = await oauth.google.authorize_access_token(request)
            nonce = request.session.get('nonce')
            userinfo = await oauth.google.parse_id_token(token, nonce=nonce)
            
            # Try to find existing user
            user = db.query(models.User).filter(models.User.google_id == userinfo['sub']).first()
            
            if user:
                # Update existing user
                user.email = userinfo['email']
                user.picture = userinfo.get('picture')
                user.last_login = datetime.utcnow()
            else:
                # Create new user
                user = models.User(
                    google_id=userinfo['sub'],
                    email=userinfo['email'],
                    picture=userinfo.get('picture')
                    # username will be set later
                )
                db.add(user)
                
            db.commit()
            
            # Store Google userinfo in session
            request.session['user'] = dict(userinfo)
            
            # If user doesn't have a username, redirect to username setup
            if not user.username:
                return RedirectResponse(url='/setup-username')
            return RedirectResponse(url='/')
            
        except Exception as e:
            print(f"Auth error: {str(e)}")
            raise HTTPException(status_code=400, detail="Could not validate credentials")

    @app.get('/logout')
    async def logout(request: Request):
        request.session.pop('user', None)
        return RedirectResponse(url='/')

    @app.get("/api/user")
    async def get_user(request: Request):
        user = request.session.get('user')
        if user:
            return {"user": user}
        else:
            return {"user": None}
        
    @app.post("/api/users/username")
    async def update_username(
        username_data: UsernameUpdate,
        request: Request,
        db: Session = Depends(get_db)
    ):
        user = await get_current_user(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Validate username
        username = username_data.username.strip()
        if len(username) < 3 or len(username) > 20:
            raise HTTPException(
                status_code=400, 
                detail="Username must be between 3 and 20 characters"
            )
        
        if not username.replace('_', '').isalnum():
            raise HTTPException(
                status_code=400, 
                detail="Username can only contain letters, numbers, and underscores"
            )
        
        try:
            user.username = username
            db.commit()
            return {"username": username}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

@app.get("/{full_path:path}")
async def serve_app(full_path: str, request: Request):
    if full_path.startswith("api"):
        # Handle API routes separately
        pass
    else:
        # Serve the main application for all non-API routes
        return FileResponse(os.path.join(static_directory, "index.html"))

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Returning response: {response.status_code}")
    return response

@app.websocket("/ws/lobby/")
async def websocket_endpoint(websocket: WebSocket):
    global connections_in_the_lobby
    await websocket.accept()
    
    # Check if user is authenticated from their session
    session_data = await websocket.get_session()
    user_info = session_data.get('user')
    
    if user_info:
        # Authenticated user
        db: Session = next(get_db())
        user = db.query(models.User).filter(models.User.google_id == user_info['sub']).first()
        player_id = str(user.id)
        player_name = user.username or f"User_{user.id}"
        is_guest = False
    else:
        # Guest user (similar to current token system)
        player_id = generate_player_token()
        player_name = f"Guest_{player_id[:6]}"
        is_guest = True
    
    connection = {
        "websocket": websocket,
        "lobby_table_id": None,
        "player_id": player_id,
        "player_name": player_name,
        "is_guest": is_guest
    }
    
    connections_in_the_lobby.append(connection)
    await websocket.send_json({
        "player_info": {
            "player_id": player_id,
            "player_name": player_name,
            "is_guest": is_guest
        }
    })
    await notify_clients_of_lobby_players()

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "create_lobby_table":
                await create_lobby_table(websocket, data, connection)
            elif action == "join_lobby_table":
                await join_lobby_table(websocket, data, connection)
            elif action == "fetch_lobby_tables":
                await fetch_lobby_tables(websocket)
            elif action == "send_message":
                await handle_chat_message(websocket, data, connection)
            elif action == "fetch_lobby_players":
                await fetch_lobby_players(websocket)
    except WebSocketDisconnect:
        await disconnect_handler(connection)

async def handle_chat_message(websocket: WebSocket, data: Dict, connection: Dict):
    message = data.get("message")
    if message:
        chat_message = {
            "action": "new_message",
            "message": {
                "sender": connection["player_name"],
                "content": message
            }
        }
        await broadcast_to_lobby(chat_message)

async def broadcast_to_lobby(message: Dict):
    for client in connections_in_the_lobby:
        await client["websocket"].send_json(message)

async def notify_clients_of_lobby_players():
    players = [{
        "id": connection["player_id"],
        "name": connection["player_name"],
        "is_guest": connection["is_guest"]
    } for connection in connections_in_the_lobby]
    message = {"action": "update_lobby_players", "players": players}
    await broadcast_to_lobby(message)

async def fetch_lobby_players(websocket: WebSocket):
    players = [{
        "id": connection["player_id"],
        "name": connection["player_name"],
        "is_guest": connection["is_guest"]
    } for connection in connections_in_the_lobby]
    await websocket.send_json({"action": "lobby_players", "players": players})

async def create_lobby_table(websocket: WebSocket, data: Dict, connection: Dict):
    db: Session = next(get_db())
    try:
        table_name = data.get("name", "New Lobby Table")
        new_lobby_table = models.LobbyTable(
            name=table_name,
            status="Waiting"
        )
        
        if connection["is_guest"]:
            new_lobby_table.player1_token = connection["player_id"]
        else:
            new_lobby_table.player1_id = int(connection["player_id"])
            
        db.add(new_lobby_table)
        db.commit()
        db.refresh(new_lobby_table)
        connection["lobby_table_id"] = new_lobby_table.id
        await notify_clients_of_lobby_table_changes()
    finally:
        db.close()

async def join_lobby_table(websocket: WebSocket, data: Dict, connection: Dict):
    db: Session = next(get_db())
    try:
        table_id = data.get("lobby_table_id")
        
        lobby_table = db.query(models.LobbyTable).filter(models.LobbyTable.id == table_id).first()
        if not lobby_table:
            await websocket.send_json({"error": "Lobby table not found"})
            return
            
        # Check if table is full
        if (lobby_table.player1_token and lobby_table.player2_token) or \
           (lobby_table.player1_id and lobby_table.player2_id):
            await websocket.send_json({"error": "Lobby table is full"})
            return
            
        # Set player based on authentication status
        if connection["is_guest"]:
            if not lobby_table.player1_token:
                lobby_table.player1_token = connection["player_id"]
            else:
                lobby_table.player2_token = connection["player_id"]
        else:
            if not lobby_table.player1_id:
                lobby_table.player1_id = int(connection["player_id"])
            else:
                lobby_table.player2_id = int(connection["player_id"])
                
        lobby_table.status = "Full"
        db.commit()
        
        connection["lobby_table_id"] = table_id
        
        if lobby_table.status == "Full":
            await start_game(lobby_table)
        else:
            await notify_clients_of_lobby_table_changes()
    finally:
        db.close()

async def fetch_lobby_tables(websocket: WebSocket):
    db: Session = next(get_db())
    try:
        lobby_tables = db.query(models.LobbyTable).all()
        lobby_tables_data = [
            {
                "id": lobby_table.id,
                "name": lobby_table.name,
                "status": lobby_table.status,
                "players": [lobby_table.player1_token, lobby_table.player2_token]
            }
            for lobby_table in lobby_tables
        ]
        await websocket.send_json({"lobby_tables": lobby_tables_data})
    finally:
        db.close()

async def notify_clients_of_lobby_table_changes():
    db: Session = next(get_db())
    try:
        lobby_tables = db.query(models.LobbyTable).all()
        lobby_tables_data = []
        
        for lobby_table in lobby_tables:
            players = []
            # Add authenticated players
            if lobby_table.player1_id:
                user = db.query(models.User).filter(models.User.id == lobby_table.player1_id).first()
                if user:
                    players.append({"id": str(user.id), "name": user.username, "is_guest": False})
            if lobby_table.player2_id:
                user = db.query(models.User).filter(models.User.id == lobby_table.player2_id).first()
                if user:
                    players.append({"id": str(user.id), "name": user.username, "is_guest": False})
                    
            # Add guest players
            if lobby_table.player1_token:
                players.append({"id": lobby_table.player1_token, "name": f"Guest_{lobby_table.player1_token[:6]}", "is_guest": True})
            if lobby_table.player2_token:
                players.append({"id": lobby_table.player2_token, "name": f"Guest_{lobby_table.player2_token[:6]}", "is_guest": True})
                
            lobby_tables_data.append({
                "id": lobby_table.id,
                "name": lobby_table.name,
                "status": lobby_table.status,
                "players": players
            })
            
        message = {"lobby_tables": lobby_tables_data}
        for client in connections_in_the_lobby:
            await client["websocket"].send_json(message)
    finally:
        db.close()

async def disconnect_handler(connection: Dict):
    connections_in_the_lobby.remove(connection)
    db: Session = next(get_db())
    try:
        lobby_table_id = connection.get("lobby_table_id")
        if lobby_table_id:
            lobby_table = db.query(models.LobbyTable).filter(models.LobbyTable.id == lobby_table_id).first()
            if lobby_table:
                db.delete(lobby_table)
                db.commit()
        await notify_clients_of_lobby_table_changes()
        await notify_clients_of_lobby_players()
    finally:
        db.close()

async def start_game(lobby_table: models.LobbyTable):
    db: Session = next(get_db())
    try:
        # Create new game with either tokens or user IDs based on player types
        game = models.Game(
            status="Waiting to Start"
        )
        
        # Set player 1
        if lobby_table.player1_id:
            game.player1_id = lobby_table.player1_id
        else:
            game.player1_token = lobby_table.player1_token
            
        # Set player 2
        if lobby_table.player2_id:
            game.player2_id = lobby_table.player2_id
        else:
            game.player2_token = lobby_table.player2_token
            
        db.add(game)
        db.commit()
        db.refresh(game)
        
        game_id = game.id
        game_engines[game_id] = GameEngine()
        game_engines[game_id].set_websocket_callbacks(
            lambda msg: send_message(game_id, msg),
            lambda state: send_game_state(game_id, state),
            lambda actions, data, color: send_available_actions(game_id, actions, data, color)
        )
        
        for client in connections_in_the_lobby:
            if client["lobby_table_id"] == lobby_table.id:
                await client["websocket"].send_json({
                    "action": "start_game",
                    "game_id": game_id,
                })
    finally:
        db.close()

def generate_player_token():
    return str(uuid.uuid4())

@app.websocket("/ws/game/")
async def websocket_game_endpoint(websocket: WebSocket):
    global connections_to_games, game_engines, current_players, game_engine

    await websocket.accept()

    if ENV == "production":
        try:
            auth_data = await websocket.receive_json()
            player_id = auth_data.get("player_id")  # Either user ID or guest token
            game_id = int(auth_data.get("game_id"))
            
            session_data = await websocket.get_session()
            user_info = session_data.get('user')
            
            db: Session = next(get_db())
            game = db.query(models.Game).filter(models.Game.id == game_id).first()
            
            if not game or game_id not in game_engines:
                await websocket.send_json({"error": "Game not found"})
                await websocket.close()
                return
            
            game_engine = game_engines[game_id]

            # Determine player color based on authentication status
            player_color = None
            player_name = None
            
            if user_info:  # Authenticated user
                user_id = int(player_id)
                if game.player1_id == user_id:
                    player_color = "red"
                    user = db.query(models.User).filter(models.User.id == user_id).first()
                    player_name = user.username or f"User_{user_id}"
                elif game.player2_id == user_id:
                    player_color = "blue"
                    user = db.query(models.User).filter(models.User.id == user_id).first()
                    player_name = user.username or f"User_{user_id}"
            else:  # Guest user
                if game.player1_token == player_id:
                    player_color = "red"
                    player_name = f"Guest_{player_id[:6]}"
                elif game.player2_token == player_id:
                    player_color = "blue"
                    player_name = f"Guest_{player_id[:6]}"
            
            if not player_color:
                await websocket.send_json({"error": "Unauthorized access"})
                await websocket.close()
                return
            
            connection = {
                "websocket": websocket,
                "game_id": game_id,
                "player_id": player_id,
                "player_name": player_name,
                "player_color": player_color,
                "is_guest": user_info is None
            }
            connections_to_games.append(connection)
            
            print(f"Player {player_name} ({player_color}) connected to game {game_id}")

            await websocket.send_json({
                "action": "initialize",
                "player_color": player_color,
                "player_name": player_name
            })

            if game.status == "Waiting to Start" and count_connections_to_game_id(game_id, connections_to_games) == 2:
                game.status = "In Progress"
                db.commit()
                asyncio.create_task(game_engines[game_id].start_game())
            else:    
                await send_game_state(game_id, game_engine.game_state)
                await game_engine.get_and_send_available_actions()
            
            while True:
                data = await websocket.receive_json()
                asyncio.create_task(game_engine.process_data_from_client(data, player_color))
                
        except WebSocketDisconnect:
            if 'connection' in locals():
                print(f"Player {connection.get('player_name', 'unknown')} disconnected from game {game_id}")
            connections_to_games[:] = [conn for conn in connections_to_games if conn["websocket"] != websocket]

    else:  # DEV environment
        try:
            if len(current_players) >= 2:
                await websocket.send_json({
                    "action": "error",
                    "message": "Game is full"
                })
                await websocket.close()
                return

            player_color = "blue" if current_players else "red"
            player_id = generate_player_token()  # Generate a guest token for dev
            player_name = f"Dev_{player_id[:6]}"

            connection = {
                "websocket": websocket,
                "player_id": player_id,
                "player_name": player_name,
                "player_color": player_color,
                "is_guest": True  # Always guest in dev
            }
            
            current_players.append(connection)
            
            await websocket.send_json({
                "action": "initialize",
                "player_color": player_color,
                "player_name": player_name
            })

            if len(current_players) == 2:
                game_engine = GameEngine()
                game_engine.set_websocket_callbacks(
                    lambda msg: send_message(None, msg),
                    lambda state: send_game_state(None, state),
                    lambda actions, data, color: send_available_actions(None, actions, data, color)
                )
                asyncio.create_task(game_engine.start_game())

            try:
                while True:
                    data = await websocket.receive_json()
                    asyncio.create_task(game_engine.process_data_from_client(data, player_color))

            except WebSocketDisconnect:
                print(f"Player {player_name} ({player_color}) disconnected")
                current_players[:] = [p for p in current_players if p["websocket"] != websocket]
                if not current_players:
                    game_engine = None

        except Exception as e:
            print(f"Error in DEV game connection: {str(e)}")
            if 'connection' in locals() and connection in current_players:
                current_players.remove(connection)

async def send_message(game_id: int, message: str):
    if ENV == "production":
        for connection in connections_to_games:
            if connection["game_id"] == game_id:
                try:
                    await connection["websocket"].send_json({
                        "action": "message",
                        "message": message,
                        "sender": connection["player_name"]  # Add sender info
                    })
                except Exception as e:
                    print(f"Error sending message to {connection['player_name']}: {str(e)}")
    else:
        for player in current_players:
            try:
                await player["websocket"].send_json({
                    "action": "message",
                    "message": message,
                    "sender": player["player_name"]  # Add sender info for DEV too
                })
            except Exception as e:
                print(f"Error sending message to {player['player_name']}: {str(e)}")

async def send_game_state(game_id: int, game_state: Dict):
    serialized_state = json.loads(serialize_game_state(game_state))
    
    if ENV == "production":
        for connection in connections_to_games:
            if connection["game_id"] == game_id:
                try:
                    await connection["websocket"].send_json({
                        "action": "update_game_state",
                        "game_state": serialized_state
                    })
                except Exception as e:
                    print(f"Error sending game state to {connection['player_name']}: {str(e)}")
    else:
        for player in current_players:
            try:
                await player["websocket"].send_json({
                    "action": "update_game_state",
                    "game_state": serialized_state
                })
            except Exception as e:
                print(f"Error sending game state to {player['player_name']}: {str(e)}")

async def send_available_actions(game_id: int, available_actions: list, current_data: str, player_color_to_send_to: str):
    if ENV == "production":
        for connection in connections_to_games:
            if (connection["game_id"] == game_id and 
                connection["player_color"] == player_color_to_send_to):
                try:
                    await connection["websocket"].send_json({
                        "action": "current_available_actions",
                        "available_actions": available_actions,
                        "current_piece_of_data_to_fill_in_current_action": current_data,
                        "player_info": {
                            "color": connection["player_color"],
                            "name": connection["player_name"]
                        }
                    })
                except Exception as e:
                    print(f"Error sending actions to {connection['player_name']}: {str(e)}")
    else:
        for player in current_players:
            if player["player_color"] == player_color_to_send_to:
                try:
                    await player["websocket"].send_json({
                        "action": "current_available_actions",
                        "available_actions": available_actions,
                        "current_piece_of_data_to_fill_in_current_action": current_data,
                        "player_info": {
                            "color": player["player_color"],
                            "name": player["player_name"]
                        }
                    })
                except Exception as e:
                    print(f"Error sending actions to {player['player_name']}: {str(e)}")

def count_connections_to_game_id(game_id: int, connections_to_games: List[Dict]) -> int:
    """Count active connections to a specific game."""
    return sum(1 for connection in connections_to_games 
              if connection["game_id"] == game_id)

def serialize_game_state(game_state: Dict) -> str:
    """Serialize game state with additional player information."""
    try:
        serialized_game_state = copy.deepcopy(game_state)
        del serialized_game_state['listeners']
        serialized_game_state["tiles"] = [tile.serialize() for tile in game_state["tiles"]]
        serialized_game_state["statuses"] = [status.serialize() for status in game_state["statuses"]]
        serialized_game_state["scorer_bonuses"] = [
            round_bonus.serialize() for round_bonus in game_state["scorer_bonuses"]
        ]
        serialized_game_state["income_bonuses"] = [
            round_bonus.serialize() for round_bonus in game_state["income_bonuses"]
        ]
        return json.dumps(serialized_game_state)
    except Exception as e:
        print(f"Error serializing game state: {str(e)}")
        return json.dumps({})

async def send_player_colors_to_clients():
    """Send initial color assignments to all players."""
    for player in current_players:
        try:
            await player["websocket"].send_json({
                "action": "initialize", 
                "player_color": player["player_color"],
                "player_name": player["player_name"],
                "is_guest": player["is_guest"]
            })
        except Exception as e:
            print(f"Error sending color to {player['player_name']}: {str(e)}")

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    user_info = request.session.get('user')
    if not user_info:
        return None
    
    return db.query(models.User).filter(models.User.google_id == user_info['sub']).first()

def count_connections_to_game_id(game_id, connections_to_games):
    return sum(1 for connection in connections_to_games if connection["game_id"] == game_id)

def print_running_tasks():
    loop = asyncio.get_running_loop()
    tasks = asyncio.all_tasks(loop)
    print(f"Number of running tasks: {len(tasks)}")

def serialize_game_state(game_state):
    serialized_game_state = copy.deepcopy(game_state)
    del serialized_game_state['listeners']
    serialized_game_state["tiles"] = [tile.serialize() for tile in game_state["tiles"]]
    serialized_game_state["statuses"] = [status.serialize() for status in game_state["statuses"]]
    serialized_game_state["scorer_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["scorer_bonuses"]]
    serialized_game_state["income_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["income_bonuses"]]
    return json.dumps(serialized_game_state)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)