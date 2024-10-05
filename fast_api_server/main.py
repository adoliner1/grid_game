from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from . import models
from .database import get_db
from .game_engine import GameEngine
from .round_bonuses import *
import json
import copy
import uuid
import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

app = FastAPI()
current_file_directory = Path(__file__).resolve().parent
static_directory = current_file_directory / "static"
if not static_directory.is_dir():
    raise RuntimeError(f"Static directory does not exist: {static_directory}")
app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")

connections_in_the_lobby: List[Dict] = []
connections_to_games: List[Dict] = []
game_engines = {}

@app.get("/")
@app.head("/")
async def read_root():
    return HTMLResponse(content="<h1>Welcome to adg!</h1>")

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    if full_path.startswith("api"):
        pass
    elif full_path.startswith("ws"):
        pass
    else:
        return FileResponse("static/index.html")

@app.websocket("/ws/lobby/")
async def websocket_endpoint(websocket: WebSocket):
    global connections_in_the_lobby
    await websocket.accept()
    player_token = generate_player_token()
    connection = {"websocket": websocket, "lobby_table_id": None, "player_token": player_token}
    connections_in_the_lobby.append(connection)
    await websocket.send_json({"player_token": player_token})
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
    except WebSocketDisconnect:
        await disconnect_handler(connection)

async def create_lobby_table(websocket: WebSocket, data: Dict, connection: Dict):
    db: Session = next(get_db())
    try:
        table_name = data.get("name", "New Lobby Table")
        new_lobby_table = models.LobbyTable(name=table_name, status="Waiting", player1_token=connection["player_token"])
        db.add(new_lobby_table)
        db.commit()
        db.refresh(new_lobby_table)
        connection["lobby_table_id"] = new_lobby_table.id
        await notify_clients()
    finally:
        db.close()

async def join_lobby_table(websocket: WebSocket, data: Dict, connection: Dict):
    db: Session = next(get_db())
    try:
        table_id = data.get("lobby_table_id")
        player_token = connection["player_token"]
       
        lobby_table = db.query(models.LobbyTable).filter(models.LobbyTable.id == table_id).first()
        if not lobby_table:
            await websocket.send_json({"error": "Lobby table not found"})
            return
       
        if lobby_table.player1_token and lobby_table.player2_token:
            await websocket.send_json({"error": "Lobby table is full"})
            return
        if not lobby_table.player1_token:
            lobby_table.player1_token = player_token
        else:
            lobby_table.player2_token = player_token
            lobby_table.status = "Full"
       
        db.commit()
       
        connection["lobby_table_id"] = table_id
       
        if lobby_table.status == "Full":
            await start_game(lobby_table)
        else:
            await notify_clients()
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

async def notify_clients():
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
            await notify_clients()
    finally:
        db.close()

async def start_game(lobby_table: models.LobbyTable):
    db: Session = next(get_db())
    try:
        game = models.Game(status="Waiting to Start", player1_token=lobby_table.player1_token, player2_token=lobby_table.player2_token)
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
    global connections_to_games, game_engines
    
    await websocket.accept()
    try:
        auth_data = await websocket.receive_json()
        player_token = auth_data.get("player_token")
        game_id = int(auth_data.get("game_id"))
        db: Session = next(get_db())
        game = db.query(models.Game).filter(models.Game.id == game_id).first()
        if not game or game_id not in game_engines:
            await websocket.send_json({"error": "Game not found"})
            await websocket.close()
            return
        
        game_engine = game_engines[game_id]

        if game.player1_token == player_token:
            player_color = "red"
        elif game.player2_token == player_token:
            player_color = "blue"
        else:
            await websocket.send_json({"error": "Unauthorized access"})
            await websocket.close()
            return
        
        connection = {
            "websocket": websocket,
            "game_id": game_id,
            "player_token": player_token,
            "player_color": player_color
        }
        connections_to_games.append(connection)
        
        print(f"Player {player_color} connected to game {game_id}")

        await websocket.send_json({
            "action": "initialize",
            "player_color": player_color
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
        if game_id:
            print(f"Player disconnected from game {game_id}")
        else:
            print(f"Player disconnected")
        connections_to_games[:] = [connection for connection in connections_to_games if connection["websocket"] != websocket]

async def send_message(game_id: int, message: str):
    for connection in connections_to_games:
        if connection["game_id"] == game_id:
            await connection["websocket"].send_json({"action": "message", "message": message})

async def send_game_state(game_id: int, game_state: Dict):
    for connection in connections_to_games:
        if connection["game_id"] == game_id:
            await connection["websocket"].send_json({
                "action": "update_game_state",
                "game_state": json.loads(serialize_game_state(game_state))
            })

async def send_available_actions(game_id: int, available_actions: list, current_data: str, player_color_to_send_to: str):
    for connection in connections_to_games:
        if connection["game_id"] == game_id and connection["player_color"] == player_color_to_send_to:
            await connection["websocket"].send_json({
                "action": "current_available_actions",
                "available_actions": available_actions,
                "current_piece_of_data_to_fill_in_current_action": current_data
            })

async def send_game_state_to_one_client(websocket: WebSocket, game_state: Dict):
    await websocket.send_json({
        "action": "update_game_state",
        "game_state": json.loads(serialize_game_state(game_state))
    })

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
    serialized_game_state["scorer_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["scorer_bonuses"]]
    serialized_game_state["income_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["income_bonuses"]]
    return json.dumps(serialized_game_state)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)