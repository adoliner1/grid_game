import random
from typing import List, Dict

from fast_api_server.tiles.tiles import Tile, AlgebraTile

class GameManager:
    def __init__(self):
        self.game_state = self.create_initial_game_state()
        self.current_turn = 0

    def create_initial_game_state(self):
        algebra_tile = AlgebraTile()
        game_state = {
            "shapes": {
                "red": {"number_of_circles": 10, "number_of_squares": 10, "number_of_triangles": 10},
                "blue": {"number_of_circles": 10, "number_of_squares": 10, "number_of_triangles": 10}
            },
            "tiles": [algebra_tile],
            "whose_turn_is_it": "red"
        }
        return game_state

    def start_round(self):
        # Run start of round tile effects
        for tile in self.game_state["tiles"]:
            tile.start_of_round_effect()

    def player_turn(self, player_color: str, action: Dict):
        # Process player action
        if action["type"] == "use_tile":
            self.use_tile(player_color, action["tile_index"])
        elif action["type"] == "place_shape":
            self.place_shape_from_storage(player_color, action["shape_type"], action["tile_index"])
        elif action["type"] == "pass":
            self.pass_turn(player_color)

    def use_tile(self, player_color: str, tile_index: int):
        tile = self.game_state["tiles"][tile_index]
        tile.use_tile(player_color)

    def place_shape_from_storage(self, player_color: str, shape_type: str, tile_index: int):
        if self.game_state["shapes"][player_color][f"number_of_{shape_type}s"] > 0:
            tile = self.game_state["tiles"][tile_index]
            next_empty_slot = tile.slots_for_shapes.index(None)
            tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
            self.game_state["shapes"][player_color][f"number_of_{shape_type}s"] -= 1

    def pass_turn(self, player_color: str):
        self.current_turn += 1
        if self.current_turn >= len(self.game_state["tiles"]):
            self.end_round()

    def end_round(self):
        # Run end of round tile effects
        for tile in self.game_state["tiles"]:
            tile.end_of_round_effect()
        self.check_end_of_game()

    def check_end_of_game(self):
        ruling_tiles = [tile for tile in self.game_state["tiles"] if tile.ruler is not None]
        if len(ruling_tiles) >= 6:
            self.end_game()

    def end_game(self):
        # Handle end of game logic
        print("Game over")
