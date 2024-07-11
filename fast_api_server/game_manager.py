import random
from typing import List, Dict, Callable
from fast_api_server.tiles.tile import Tile
from fast_api_server.tiles.algebra import Algebra
from fast_api_server.tiles.boron import Boron
from fast_api_server.tiles.pluto import Pluto
from fast_api_server.tiles.prince import Prince
from fast_api_server.game_utilities import get_other_player_color, determine_rulers

class GameManager:

    shapeHierarchy = {
        'circle': 1,
        'square': 2,
        'triangle': 3
    }

    def __init__(self):
        self.notify_clients_of_new_log_callback = None
        self.notify_clients_of_new_game_state_callback = None

    def set_notify_clients_of_new_log_callback(self, callback: Callable[[str], None]):
        self.notify_clients_of_new_log_callback = callback

    def set_notify_clients_of_new_game_state_callback(self, callback: Callable[[str], None]):
        self.notify_clients_of_new_game_state_callback = callback

    async def start_round(self, game_state):
        await self.notify_clients_of_new_log_callback("Starting new round")

        round = game_state["round"] 
        if (round > 0):
            game_state["round_bonuses"][round-1].cleanup(game_state)
        game_state["round_bonuses"][round].setup(game_state)

        if game_state['first_player']:
            game_state['whose_turn_is_it'] = game_state['first_player']
        else:
            game_state['whose_turn_is_it'] = 'red'           
        game_state['first_player'] = None
        game_state['player_has_passed']['red'] = False
        game_state['player_has_passed']['blue'] = False
        for tile in game_state["tiles"]:
            await tile.start_of_round_effect(game_state, self.notify_clients_of_new_log_callback)

        determine_rulers(game_state)

    async def player_takes_use_tile_action(self, game_state, tile_index, player_color, **kwargs):

        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return
        
        tile = game_state["tiles"][tile_index]
        await tile.use_tile(game_state, player_color, self.notify_clients_of_new_log_callback, **kwargs)
        determine_rulers(game_state)
        if game_state["player_has_passed"][get_other_player_color(player_color)] == False:
            game_state["whose_turn_is_it"] = get_other_player_color(player_color)
            await self.notify_clients_of_new_log_callback(f"Turn passes to {game_state['whose_turn_is_it']} player")
        else:
            await self.notify_clients_of_new_log_callback(f"{get_other_player_color(player_color)} has passed, turn remains with {player_color}")

        await self.notify_clients_of_new_game_state_callback()

    async def player_takes_place_on_slot_on_tile_action(self, game_state, player_color, slot_index, tile_index, shape_type):
        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return

        tile = game_state["tiles"][tile_index]
        slot = tile.slots_for_shapes[slot_index]

        if slot and self.shapeHierarchy[shape_type] <= self.shapeHierarchy[slot['shape']]:
            await self.notify_clients_of_new_log_callback("Cannot place on this slot")
            return

        if game_state["shapes"][player_color][f"number_of_{shape_type}s"] <= 0:
            await self.notify_clients_of_new_log_callback(f"No {shape_type}s in storage")
            return

        game_state["shapes"][player_color][f"number_of_{shape_type}s"] -= 1

        await tile.place_shape_at_index(game_state, slot_index, shape_type, player_color, self.notify_clients_of_new_log_callback)

        for listener_name, listener_function in game_state["listeners"]["on_place"].items():
            await listener_function(game_state, self.notify_clients_of_new_log_callback, placer=player_color, shape=shape_type, index_of_tile_placed_at=tile_index)  

        determine_rulers(game_state)

        if game_state["player_has_passed"][get_other_player_color(player_color)] == False:
            game_state["whose_turn_is_it"] = get_other_player_color(player_color)
            await self.notify_clients_of_new_log_callback(f"Turn passes to {game_state['whose_turn_is_it']} player")
        else:
            await self.notify_clients_of_new_log_callback(f"{get_other_player_color(player_color)} has passed, turn remains with {player_color}")

        await self.notify_clients_of_new_game_state_callback()

    async def player_passes(self, game_state, player_color):
        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return
        
        await self.notify_clients_of_new_log_callback(f"{player_color} passes")
        game_state["player_has_passed"][player_color] = True

        if game_state["player_has_passed"][get_other_player_color(player_color)] == False:
            await self.notify_clients_of_new_log_callback(f"{player_color} is first player to pass this round and becomes first player")
            game_state["first_player"] = player_color

        if game_state["player_has_passed"]["red"] and game_state["player_has_passed"]["blue"]:
            await self.end_round(game_state)

        else:
            game_state["whose_turn_is_it"] = get_other_player_color(player_color)
            await self.notify_clients_of_new_log_callback(f"turn passes to {game_state['whose_turn_is_it']}")

        await self.notify_clients_of_new_game_state_callback()

    async def end_round(self, game_state):
        await self.notify_clients_of_new_log_callback(f"both players have passed, ending round")

        for tile in game_state["tiles"]:
            await tile.end_of_round_effect(game_state, self.notify_clients_of_new_log_callback)

        determine_rulers(game_state)

        if not await self.check_for_end_of_game(game_state):
            game_state["round"] += 1
            await self.start_round(game_state)

    async def check_for_end_of_game(self, game_state):
        await self.notify_clients_of_new_log_callback(f"checking for end of game")
        tiles_with_a_ruler = [tile for tile in game_state["tiles"] if tile.determine_ruler(game_state) is not None]
        if len(tiles_with_a_ruler) >= 7:
           await self.notify_clients_of_new_log_callback(f"7 or more tiles have a ruler, ending game")
           self.end_game(game_state)
           return True
        if (game_state["round"] == 5):
            await self.notify_clients_of_new_log_callback(f"Round 5, ending game")
            return True
        
        return False

    async def end_game(self, game_state):
        await self.notify_clients_of_new_log_callback("Game over. Doing end game scoring")
        for tile in game_state["tiles"]:
            await tile.end_of_game_effect(game_state, self.notify_clients_of_new_log_callback)