from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import inspect
import models
from database import get_db
from tiles.tile import Tile
from tiles.algebra import Algebra
from tiles.boron import Boron
from tiles.carbon import Carbon
from tiles.waterfalls import Waterfalls
from tiles.queen import Queen
from tiles.king import King
from tiles.plains import Plains
from tiles.jupiter import Jupiter
from tiles.saturn import Saturn
from tiles.pluto import Pluto
from tiles.duke import Duke
from tiles.nitrogen import Nitrogen
from tiles.sword import Sword
from tiles.spear import Spear
from tiles.jester import Jester
from tiles.prince import Prince
from tiles.caves import Caves
from tiles.combinatorics import Combinatorics
from tiles.geometry import Geometry
from game_manager import GameManager
from round_bonuses import *
import json
import random
import os
import importlib
import sys

app = FastAPI()
connected_clients: List[Dict] = []
local_game_state = None
currentPlayers = []
currentUseTileRequest = {}
game_manager = GameManager()

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
    
    async def notify_clients_of_new_log(message):
        for player in currentPlayers:
            await player["websocket"].send_json({
                "action": "message", 
                "message": message
            })

    async def notify_clients_of_new_game_state():
        for player in currentPlayers:
            await player["websocket"].send_json({
                "action": "update_game_state",
                "game_state": json.loads(serialize_game_state(local_game_state))
            })

    global local_game_state
    global currentPlayers
    global currentUseTileRequest
    game_manager.set_notify_clients_of_new_log_callback(notify_clients_of_new_log)
    game_manager.set_notify_clients_of_new_game_state_callback(notify_clients_of_new_game_state)

    #this will all be done in lobby
    await websocket.accept()
    if not local_game_state:
        local_game_state = create_initial_game_state()
        setup_tile_listeners(local_game_state)
    if len(currentPlayers) >= 2:
        await websocket.send_json({
            "action": "error",
            "message": "Game is full"
        })
        await websocket.close()
        return
    
    if len(currentPlayers) == 1:
        existing_player_color = currentPlayers[0]["color"]
        player_color = "blue" if existing_player_color == "red" else "red"
    else:
        player_color = "red"
    
    currentPlayers.append({"websocket": websocket, "color": player_color})
    await websocket.send_json({
        "action": "initialize",
        "game_state": json.loads(serialize_game_state(local_game_state)),
        "player_color": player_color
    })

    if len(currentPlayers) == 2:
        await game_manager.start_round(local_game_state)
        await notify_clients_of_new_game_state()
    # ^^^ this will all be done in lobby ^^^

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            
            #determine player color
            player_color = None
            for player in currentPlayers:
                if player["websocket"] == websocket:
                    player_color = player["color"]
                    break

            if player_color is None:
                await websocket.send_json({"action": "error", "message": "Player not found in game"})
                continue

            await game_manager.perform_conversions(local_game_state, player_color, data.get("conversions"))

            action = data.get("action")

            if action == "place_shape_on_slot":

                tile_index = data.get("tile_and_slot_to_place_on").get("tile")
                slot_index = data.get("tile_and_slot_to_place_on").get("slot")
                shape_type = data.get("shape_type")

                await game_manager.player_takes_place_on_slot_on_tile_action(local_game_state, player_color, slot_index, tile_index, shape_type)

            elif action == 'use_tile':

                tile_index_to_use = data.get("tile_index_to_use")
                await game_manager.player_takes_use_tile_action(local_game_state, tile_index_to_use, player_color, **data)               

            elif action == "pass":
                await game_manager.player_passes(local_game_state, player_color)

            elif action == 'update_use_tile_data':
                pass
            else:
                await websocket.send_json({"action": "error", "message": "Unknown action"})
    except WebSocketDisconnect:
        currentPlayers = [p for p in currentPlayers if p["websocket"] != websocket]
        if len(currentPlayers) == 0:
            local_game_state = None
        print(f"{player_color} player disconnected")

def import_all_tiles_from_folder(folder_name):
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    tile_classes = []
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    module_names = [f[:-3] for f in os.listdir(folder_path) if f.endswith('.py') and f != '__init__.py']
    
    for module_name in module_names:
        module = importlib.import_module(f'{folder_name}.{module_name}')
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, Tile) and attribute is not Tile:
                tile_classes.append(attribute)
    
    return tile_classes

def get_all_round_bonuses():
    module_name = 'round_bonuses'
    module = importlib.import_module(module_name)
    
    round_bonus_classes = []
    
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, RoundBonus) and obj is not RoundBonus:
            round_bonus_classes.append(obj)
    
    return round_bonus_classes

def create_initial_game_state():
    all_round_bonuses = get_all_round_bonuses()
    all_tiles = import_all_tiles_from_folder('tiles')
    chosen_tiles = random.sample(all_tiles, 9)
    chosen_round_bonuses = [random.choice(all_round_bonuses)() for _ in range(6)]

    game_state = {
        "round": 0,
        "shapes": {
            "red": { "number_of_circles": 0, "number_of_squares": 0, "number_of_triangles": 0 },
            "blue": { "number_of_circles": 1, "number_of_squares": 0, "number_of_triangles": 0 }
        },
        "points": {
            "red": 0,
            "blue": 0
        },
        "player_has_passed": {
            "red": False,
            "blue": False,
        },
        "tiles": [tile() for tile in chosen_tiles],
        "whose_turn_is_it": "red",
        "first_player": "red",
        "round_bonuses": chosen_round_bonuses,
        "listeners": {"on_place": {}, "start_of_round": {}, "end_of_round": {}, "on_produce": {}},
    }

    return game_state

def setup_tile_listeners(game_state):
    for tile in game_state["tiles"]:
        if hasattr(tile, 'setup_listener'):
            tile.setup_listener(game_state)

def serialize_game_state(game_state):
    serialized_game_state = game_state.copy()
    del serialized_game_state['listeners'] #delete listeners, it's a server only piece of game_state
    serialized_game_state["tiles"] = [tile.serialize() for tile in game_state["tiles"]]
    serialized_game_state["round_bonuses"] = [round_bonus.serialize() for round_bonus in game_state["round_bonuses"]]
    return json.dumps(serialized_game_state)