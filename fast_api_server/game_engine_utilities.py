from typing import List, Dict, OrderedDict
import game_action_container
import round_bonuses
import json
import random
import os
import importlib
import sys
import asyncio
import inspect
import game_constants
from tiles.tile import Tile

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
        if issubclass(obj, round_bonuses.RoundBonus) and obj is not round_bonuses.RoundBonus:
            round_bonus_classes.append(obj)
    
    return round_bonus_classes

#place the shape on the tile. 
#if it overwrote another shape, create and push a game action container asking the owning player to place it on a powerup
#call wait on the current game action container   
async def place_shape_on_tile(game_state, game_action_container_stack, tile_index, slot_index, shape, color, send_clients_new_log_message):
    tile_to_place_on = game_state["tiles"][tile_index]
    slot_to_place_on = tile_to_place_on.slots_for_shapes[slot_index]
    if slot_to_place_on:
        old_slot = slot_to_place_on

    slot_to_place_on = {'shape': shape, 'color': color}
    await send_clients_new_log_message(f"{color} placed a {shape} on {tile_to_place_on.name}")

    if old_slot:
        reaction_container_to_place_trumped_shape_on_a_powerup = game_action_container.GameActionContainer(
                                    event = asyncio.Event(),
                                    game_action = "place_shape_on_a_powerup",
                                    required_data_for_action = {"powerup_slot_to_place_on": {}, "shape_type_to_place": old_slot["shape"]},
                                    whose_action = old_slot["color"])
        
        game_action_container_stack.append(reaction_container_to_place_trumped_shape_on_a_powerup)
        await game_action_container_stack[-1].event.wait()

    for listener_name, listener_function in game_state["listeners"]["on_place"].items():
        await listener_function(game_state, send_clients_new_log_message, placer=color, shape=shape, index_of_tile_placed_at=tile_index)  

def create_new_game_state():
    
    all_round_bonuses = get_all_round_bonuses()
    all_tiles = import_all_tiles_from_folder('tiles')
    chosen_tiles = random.sample(all_tiles, 9)
    chosen_round_bonuses = [random.choice(all_round_bonuses)() for _ in range(6)]
    chosen_powerups = None #TODO
    game_state = {
        "round": 0,
        "shapes_in_storage": {
            "red": { "circle": 0, "square": 0, "triangle": 0 },
            "blue": { "circle": 0, "square": 0, "triangle": 0 }
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
        "powerups": {
            "red": chosen_powerups, #need copy? 
            "blue": chosen_powerups, #need copy? 
        },
        "round_bonuses": chosen_round_bonuses,
    }

    return game_state

def create_initial_decision_game_action_container(whose_turn_is_it):
    return GameActionContainer(
            event=asyncio.Event(),
            game_action="initial_decision",
            required_data_for_action={"initial_decision": None},
            whose_action=whose_turn_is_it,
        )