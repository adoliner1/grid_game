from typing import Callable
from game_utilities import *

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

    def get_available_actions(self, game_state, current_action, current_piece_of_data_to_fill_in_current_action):
        available_actions_with_details = {"pass": []}

        if current_action:
            if current_action["action"] == 'place_shape_on_slot':
                shape_type_to_place = current_action["shape_type_to_place"]
                slots_that_can_be_placed_on = get_slots_that_can_be_placed_on(game_state, shape_type_to_place)
                available_actions_with_details["select_a_slot"] = slots_that_can_be_placed_on

            elif current_action["action"] == 'use_tile':
                index_of_tile_in_use = current_action["index_of_tile_in_use"]
                tile_in_use = game_state["tiles"][index_of_tile_in_use]
                tile_in_use.set_available_actions(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details)

        #indicates we're in the initial state. Both selecting a shape from storage or a useable tile are options
        else:
            whose_turn_is_it = game_state['whose_turn_is_it']
            available_actions_with_details['select_a_shape_in_storage'] = []
            available_actions_with_details['select_a_tile'] = []

            for shape, amount in game_state["shapes_in_storage"][whose_turn_is_it].items():
                if amount > 0:
                    available_actions_with_details["select_a_shape_in_storage"].append(shape)

            for tile_index, tile in enumerate(game_state["tiles"]):
                if tile.is_useable(game_state):
                    available_actions_with_details['select_a_tile'].append(tile_index)
                
        return available_actions_with_details

    async def perform_conversions(self, local_game_state, player_color, conversions):
        if local_game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback(f"It's not {player_color}'s turn.")
            return

        for conversion in conversions:
                match conversion:
                    case "circle to square":
                        if local_game_state["shapes_in_storage"][player_color]["circle"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["circle"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.notify_clients_of_new_log_callback(f"{player_color} converts 3 circles to a square")
                        else:
                            await self.notify_clients_of_new_log_callback(f"{player_color} tries to convert 3 circles to a square but doesn't have enough circles")
                    case "square to triangle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["triangle"] += 1
                            await self.notify_clients_of_new_log_callback(f"{player_color} converts 3 squares to a triangle")
                        else:
                            await self.notify_clients_of_new_log_callback(f"{player_color} tries to convert 3 squares to a triangle but doesn't have enough squares")

                    case "triangle to square":
                        if local_game_state["shapes_in_storage"][player_color]["triangle"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["triangle"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.notify_clients_of_new_log_callback(f"{player_color} converts 1 triangle to a square")
                        else:
                            await self.notify_clients_of_new_log_callback(f"{player_color} tries to convert a triangle to a square but doesn't have enough triangles")

                    case "square to circle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["circle"] += 1
                            await self.notify_clients_of_new_log_callback(f"{player_color} converts 1 square to 1 circle")
                        else:
                            await self.notify_clients_of_new_log_callback(f"{player_color} tries to convert a square to a circle but doesn't have enough squares")

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

        #give base income
        await self.give_base_income_to_players(game_state)
        determine_rulers(game_state)

    async def give_base_income_to_players(self, game_state):
        shapes_to_give = [
            ('circle', 2),
            ('square', 1),
            ('triangle', 1)
        ]

        player_colors = ["red", "blue"]

        await self.notify_clients_of_new_log_callback("Giving base income")
        for player_color in player_colors:
            for shape, amount in shapes_to_give:
                await produce_shape_for_player(game_state, player_color, amount, shape, None)

    async def player_takes_use_tile_action(self, game_state, tile_index, player_color, **data):

        if game_state["whose_turn_is_it"] != player_color:
            await self.notify_clients_of_new_log_callback("Not your turn")
            return
        
        tile = game_state["tiles"][tile_index]
        # if use tile returns false, the action failed, so don't update the rest of the game state
        if not await tile.use_tile(game_state, player_color, self.notify_clients_of_new_log_callback, **data):
            return
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

        if game_state["shapes_in_storage"][player_color][shape_type] <= 0:
            await self.notify_clients_of_new_log_callback(f"No {shape_type}s in storage")
            return

        game_state["shapes_in_storage"][player_color][shape_type] -= 1

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

        for listener_name, listener_function in game_state["listeners"]["end_of_round"].items():
            await listener_function(game_state, self.notify_clients_of_new_log_callback)  

        determine_rulers(game_state)

        if not await self.check_for_end_of_game(game_state):
            game_state["round"] += 1
            await self.start_round(game_state)

    async def check_for_end_of_game(self, game_state):
        await self.notify_clients_of_new_log_callback(f"checking for end of game")
        tiles_with_a_ruler = [tile for tile in game_state["tiles"] if tile.determine_ruler(game_state) is not None]
        if len(tiles_with_a_ruler) >= 7:
           await self.notify_clients_of_new_log_callback(f"7 or more tiles have a ruler, ending game")
           await self.end_game(game_state)
           return True
        if (game_state["round"] == 5):
            await self.notify_clients_of_new_log_callback(f"Round 5, ending game")
            await self.end_game(game_state)
            return True
        
        return False

    async def end_game(self, game_state):
        for tile in game_state["tiles"]:
            await tile.end_of_game_effect(game_state, self.notify_clients_of_new_log_callback)

        await self.notify_clients_of_new_game_state_callback()
        await self.notify_clients_of_new_log_callback(f"Final Score: Red: {game_state['points']['red']} Blue: {game_state['points']['blue']}")

        if game_state["points"]["red"] > game_state["points"]["blue"]:
            await self.notify_clients_of_new_log_callback("Red wins!")
        elif game_state["points"]["blue"] > game_state["points"]["red"]:
            await self.notify_clients_of_new_log_callback("Blue wins!")
        else:
            await self.notify_clients_of_new_log_callback("It's a tie!")
