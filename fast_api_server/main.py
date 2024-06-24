from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from fast_api_server import models
from fast_api_server.database import get_db
import random

app = FastAPI()
connected_clients: List[Dict] = []
local_game_state = None

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
    global local_game_state
    await websocket.accept()
    if not local_game_state:
        local_game_state = create_initial_game_state()
    
    if len(local_game_state["players"]) >= 2:
        await websocket.send_json({"error": "Game is full"})
        await websocket.close()
        return
    
    if len(local_game_state["players"]) == 1:
        existing_player_color = local_game_state["players"][0]["color"]
        player_color = "blue" if existing_player_color == "red" else "red"
    else:
        player_color = "red"
    
    local_game_state["players"].append({"websocket": websocket, "color": player_color})
    await websocket.send_json({
        "game_state": local_game_state["game_state"],
        "player_color": player_color
    })  # Send the game state and player color

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json(f"Received: {data}")
    except WebSocketDisconnect:
        local_game_state["players"] = [p for p in local_game_state["players"] if p["websocket"] != websocket]
        if len(local_game_state["players"]) == 0:
            local_game_state = None
        print(f"{player_color} player disconnected")


def create_initial_game_state():
    game_state = {
        "players": [],
        "game_state": {
            "shapes": {
                "player1": { "number_of_circles": 1, "number_of_squares": 0, "number_of_triangles": 0 },
                "player2": { "number_of_circles": 1, "number_of_squares": 0, "number_of_triangles": 0 }
            },
            "tiles": [
                {
                    "name": f"Tile {index + 1}",
                    "description": f"This is tile {index + 1}",
                    "ruling_criteria": f"Criterion {index + 1}",
                    "ruling_benefits": f"Benefit {index + 1}",
                    "slots_for_shapes": [None] * random.randint(1, 5)
                } for index in range(9)
            ],
            "whose_turn_is_it": "red"
        }
    }
    return game_state
