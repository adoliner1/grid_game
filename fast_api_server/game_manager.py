import random
from typing import List, Dict, Callable
from fast_api_server.tiles.tiles import Tile, Algebra, Boron

class GameManager:
    def __init__(self):
        self.notify_clients_of_new_log_callback = None
        self.notify_clients_of_new_game_state_callback = None

    def set_notify_clients_of_new_log_callback(self, callback: Callable[[str], None]):
        self.notify_clients_of_new_log_callback = callback

    def set_notify_clients_of_new_game_state_callback(self, callback: Callable[[str], None]):
        self.notify_clients_of_new_game_state_callback = callback

    async def start_round(self, game_state):
        await self.notify_clients_of_new_log_callback("Starting new round")
        if game_state['first_player']:
            game_state['whose_turn_is_it'] = game_state['first_player']
        else:
            game_state['whose_turn_is_it'] = 'red'           
        game_state['first_player'] = None
        game_state['player_has_passed']['red'] = False
        game_state['player_has_passed']['blue'] = False
        for tile in game_state["tiles"]:
            await tile.start_of_round_effect(game_state, self.notify_clients_of_new_log_callback)

    async def player_takes_place_shape_on_tile_action(self, game_state, player_color, tile_index, shape_type):
        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return

        tile = game_state["tiles"][tile_index]
        if None not in tile.slots_for_shapes:
            await self.notify_clients_of_new_log_callback("No empty slots on this tile")
            return

        if game_state["shapes"][player_color][f"number_of_{shape_type}s"] <= 0:
            await self.notify_clients_of_new_log_callback(f"No {shape_type}s in storage")
            return

        game_state["shapes"][player_color][f"number_of_{shape_type}s"] -= 1
        next_empty_slot = tile.slots_for_shapes.index(None)
        tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
        await self.notify_clients_of_new_log_callback(f"{player_color} placed a {shape_type} on tile {tile_index}")

        if game_state["player_has_passed"][self.get_other_player_color(player_color)] == False:
            game_state["whose_turn_is_it"] = self.get_other_player_color(player_color)
            await self.notify_clients_of_new_log_callback(f"turn passes to {game_state['whose_turn_is_it']} player")
        else:
            await self.notify_clients_of_new_log_callback(f"{self.get_other_player_color(player_color)} has passed, turn remains with {player_color}")
        await self.notify_clients_of_new_game_state_callback()

    async def player_passes(self, game_state, player_color):
        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return
        
        await self.notify_clients_of_new_log_callback(f"{player_color} passes")
        game_state["player_has_passed"][player_color] = True

        if game_state["player_has_passed"][self.get_other_player_color(player_color)] == False:
            await self.notify_clients_of_new_log_callback(f"{player_color} is first player to pass this round and becomes first player")
            game_state["first_player"] = player_color

        if game_state["player_has_passed"]["red"] and game_state["player_has_passed"]["blue"]:
            await self.end_round(game_state)

        else:
            game_state["whose_turn_is_it"] = self.get_other_player_color(player_color)
            await self.notify_clients_of_new_log_callback(f"turn passes to {game_state['whose_turn_is_it']}")

        await self.notify_clients_of_new_game_state_callback()

    async def end_round(self, game_state):
        await self.notify_clients_of_new_log_callback(f"both players have passed, ending round")

        for tile in game_state["tiles"]:
            await tile.end_of_round_effect(game_state, self.notify_clients_of_new_log_callback)

        if not await self.check_for_end_of_game(game_state):
            await self.start_round(game_state)

    async def check_for_end_of_game(self, game_state):
        await self.notify_clients_of_new_log_callback(f"checking for end of game")
        # ruling_tiles = [tile for tile in self.game_state["tiles"] if tile.ruler is not None]
        # if len(ruling_tiles) >= 6:
        #   self.end_game(game_state)
        #   return True
        return False

    def end_game(self, game_state):
        # Handle end of game logic
        print("Game over")

    def get_other_player_color(self, player_color):
        return 'blue' if player_color == 'red' else 'red'