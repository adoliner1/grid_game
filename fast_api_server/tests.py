import pytest
from tiles.tile import Tile
from tiles.stone_shrine import Algebra
from tiles.boron import Boron
from tiles.altar_of_hades import Pluto
from tiles.sword import Sword
from tiles.prince import Prince
from tiles.caves import Caves
from game_manager import GameManager
from round_bonuses import PointsPerCircle
from game_utilities import *

# Utilities
def get_test_game_state_1():
    return {
        "round": 0,
        "shapes": {
            "red": { "number_of_circles": 10, "number_of_squares": 10, "number_of_triangles": 10 },
            "blue": { "number_of_circles": 10, "number_of_squares": 10, "number_of_triangles": 10 }
        },
        "points": {
            "red": 0,
            "blue": 0
        },
        "player_has_passed": {
            "red": False,
            "blue": False,
        },
        "tiles": [
            Algebra(), Boron(), Pluto(), Sword(), Prince(), Caves()
        ],
        "whose_turn_is_it": "red",
        "first_player": None,
        "round_bonuses": [PointsPerCircle(), PointsPerCircle(), PointsPerCircle(), PointsPerCircle(), PointsPerCircle()],
        "listeners": {"on_place": {}, "start_of_round": {}, "end_of_round": {}},
    }

def setup_tile_listeners(game_state):
    for tile in game_state["tiles"]:
        if hasattr(tile, 'setup_listener'):
            tile.setup_listener(game_state)

async def print_log(message):
    print(message)

async def no_op():
    pass

@pytest.fixture(scope="function")
def game_manager():
    game_manager = GameManager()
    game_manager.set_notify_clients_of_new_log_callback(print_log)
    game_manager.set_notify_clients_of_new_game_state_callback(no_op)
    return game_manager

@pytest.fixture(scope="function")
def game_state():
    game_state = get_test_game_state_1()
    setup_tile_listeners(game_state)
    return game_state

@pytest.mark.asyncio
async def test_pluto(game_manager, game_state):
    await game_manager.player_takes_place_on_slot_on_tile_action(game_state, "red", 0, 2, "circle")
    await game_manager.player_passes(game_state, "blue")
    await game_manager.player_takes_place_on_slot_on_tile_action(game_state, "red", 1, 2, "circle")
    await game_manager.player_takes_place_on_slot_on_tile_action(game_state, "red", 2, 2, "circle")
    assert game_state["tiles"][2].ruler == "red", "Red should be ruler"
    await game_manager.player_takes_use_tile_action(game_state, 2, "red")
    assert game_state["shapes"]["red"]["number_of_squares"] == 11, "Red should have gained a square and have 11"
    assert count_number_of_shape_for_player_on_tile("circle", "red", game_state["tiles"][2]) == 2, "red should have 2 circles on pluto now"

if __name__ == "__main__":
    pytest.main()