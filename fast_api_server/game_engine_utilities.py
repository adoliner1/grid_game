from typing import List, Dict
from game_action_container import GameActionContainer
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
        "powerups": chosen_powerups,
        "round_bonuses": chosen_round_bonuses,
    }

    return game_state

def create_new_turn_game_action_container(whose_turn_is_it):
    return GameActionContainer(
            asyncio.Event(),
            game_action="new_turn_choice",
            required_data_for_action={"choice": None},
            whose_action=whose_turn_is_it
        )
