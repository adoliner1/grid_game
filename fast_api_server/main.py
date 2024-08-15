from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import models
from database import get_db
from game_engine import GameEngine
from round_bonuses import *
import json
import copy

app = FastAPI()
connected_clients: List[Dict] = []
current_players = []
game_engine = None

@app.websocket("/ws/lobby/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection = {"websocket": websocket, "lobby_table_id": None}
    connected_clients.append(connection)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "create_lobby_table":
                await create_lobby_table(websocket, data, connection)
            elif action == "join_lobby_table":
                await join_lobby_table(websocket, data)
            elif action == "fetch_lobby_tables":
                await fetch_lobby_tables(websocket)
    except WebSocketDisconnect:
        await disconnect_handler(connection)

async def create_lobby_table(websocket: WebSocket, data: Dict, connection: Dict):
    db: Session = next(get_db())
    table_name = data.get("name", "New Lobby Table")
    new_lobby_table = models.LobbyTable(name=table_name, status="Waiting")
    db.add(new_lobby_table)
    db.commit()
    db.refresh(new_lobby_table)
    connection["lobby_table_id"] = new_lobby_table.id
    await notify_clients()

async def join_lobby_table(websocket: WebSocket, data: Dict):
    db: Session = next(get_db())
    table_id = data.get("lobby_table_id")
    player_name = data.get("player_name")
    lobby_table = db.query(models.LobbyTable).filter(models.LobbyTable.id == table_id).first()
    if not lobby_table:
        await websocket.send_json({"error": "Lobby table not found"})
        return
    
    player = db.query(models.Player).filter(models.Player.name == player_name).first()
    if not player:
        player = models.Player(name=player_name, lobby_table_id=table_id)
        db.add(player)
        db.commit()
        db.refresh(player)
    else:
        player.lobby_table_id = table_id
        db.commit()
    await notify_clients()

async def fetch_lobby_tables(websocket: WebSocket):
    db: Session = next(get_db())
    lobby_tables = db.query(models.LobbyTable).all()
    lobby_tables_data = [
        {
            "id": lobby_table.id,
            "name": lobby_table.name,
            "status": lobby_table.status,
            "players": [{"id": player.id, "name": player.name} for player in lobby_table.players]
        }
        for lobby_table in lobby_tables
    ]
    await websocket.send_json({"lobby_tables": lobby_tables_data})

async def notify_clients():
    db: Session = next(get_db())
    lobby_tables = db.query(models.LobbyTable).all()
    lobby_tables_data = [
        {
            "id": lobby_table.id,
            "name": lobby_table.name,
            "status": lobby_table.status,
            "players": [{"id": player.id, "name": player.name} for player in lobby_table.players]
        }
        for lobby_table in lobby_tables
    ]
    message = {"lobby_tables": lobby_tables_data}
    for client in connected_clients:
        await client["websocket"].send_json(message)

async def disconnect_handler(connection: Dict):
    connected_clients.remove(connection)
    db: Session = next(get_db())
    lobby_table_id = connection.get("lobby_table_id")
    if lobby_table_id:
        lobby_table = db.query(models.LobbyTable).filter(models.LobbyTable.id == lobby_table_id).first()
        if lobby_table:
            db.delete(lobby_table)
            db.commit()
        await notify_clients()

@app.websocket("/ws/game/")
async def websocket_game_endpoint(websocket: WebSocket):
    global game_engine, current_players

    await websocket.accept()
    if len(current_players) >= 2:
        await websocket.send_json({
            "action": "error",
            "message": "Game is full"
        })
        await websocket.close()
        return

    player_color = "blue" if current_players else "red"
    current_players.append({"websocket": websocket, "color": player_color})

    if len(current_players) == 2:
        await send_player_colors_to_clients()
        game_engine = GameEngine()
        game_engine.set_websocket_callbacks(send_clients_new_log_message, send_clients_new_game_state, send_available_actions_to_client)
        asyncio.create_task(game_engine.start_game())

    try:
        while True:
            data = await websocket.receive_json()
            asyncio.create_task(game_engine.process_data_from_client(data, player_color))

    except WebSocketDisconnect:
        current_players = [p for p in current_players if p["websocket"] != websocket]
        print(f"{player_color} player disconnected")
        if not current_players:
            game_engine = None

async def send_clients_new_log_message(message):
        for player in current_players:
            await player["websocket"].send_json({
                "action": "message", 
                "message": message
            })

async def send_player_colors_to_clients():
    for player in current_players:
        if player["color"] == "blue":
            await player["websocket"].send_json({
                "action": "initialize", 
                "player_color": "blue"
            })
        else:
            await player["websocket"].send_json({
                "action": "initialize", 
                "player_color": "red"
            })

async def send_clients_new_game_state(game_state):
    for player in current_players:
        await player["websocket"].send_json({
            "action": "update_game_state",
            "game_state": json.loads(serialize_game_state(game_state))
        })

async def send_available_actions_to_client(available_actions, current_piece_of_data_to_fill_in_current_action, player_color_to_send_to):
    for player in current_players:
        if player["color"] == player_color_to_send_to:
            await player["websocket"].send_json({
                "action": "current_available_actions",
                "available_actions": available_actions,
                "current_piece_of_data_to_fill_in_current_action": current_piece_of_data_to_fill_in_current_action
            })

def print_running_tasks():
    loop = asyncio.get_running_loop()
    tasks = asyncio.all_tasks(loop)
    print(f"Number of running tasks: {len(tasks)}")

def serialize_game_state(game_state):
    serialized_game_state = copy.deepcopy(game_state)
    del serialized_game_state['listeners'] #delete listeners, it's a server only piece of game_state
    serialized_game_state["tiles"] = [tile.serialize() for tile in game_state["tiles"]]
    serialized_game_state["round_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["round_bonuses"]]
    serialized_game_state["powerups"]["red"] = [powerup.serialize() for powerup in game_state["powerups"]["red"]]
    serialized_game_state["powerups"]["blue"] = [powerup.serialize() for powerup in game_state["powerups"]["blue"]]
    return json.dumps(serialized_game_state)