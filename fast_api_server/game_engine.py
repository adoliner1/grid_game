from typing import Callable, List, OrderedDict
import game_utilities
import game_engine_utilities
import game_constants
import game_action_container
import asyncio

class GameEngine:

    def __init__(self):
        self.game_state = game_engine_utilities.create_new_game_state()
        self.send_clients_new_log_message = None
        self.send_clients_new_game_state = None
        self.send_available_client_actions = None
        self.game_action_container_stack = List[game_action_container.GameActionContainer]
        self.listeners = {"on_place": {}, "start_of_round": {}, "end_of_round": {}, "on_produce": {}}
        self.game_has_ended = False
    
    def set_websocket_callbacks(self, send_clients_new_log_message, send_clients_new_game_state, send_available_client_actions_to_client):
        self.send_clients_new_log_message = send_clients_new_log_message
        self.send_clients_new_game_state = send_clients_new_game_state
        self.send_available_client_actions_to_client = send_available_client_actions_to_client

    async def run_game_loop(self):
        while not self.game_has_ended:
            if not self.game_action_container_stack:
                self.game_action_container_stack.push(game_engine_utilities.create_initial_decision_game_action_container(self.game_state.whose_turn_is_it))
            
            current_game_action_container = self.game_action_container_stack[-1]
            next_piece_of_data_to_fill = current_game_action_container.get_next_piece_of_data_to_fill()

            if not next_piece_of_data_to_fill:
                await self.execute_game_action(self.game_action_container_stack.pop())
            else:
                await self.send_available_client_actions(self.get_available_client_actions("red", current_game_action_container, next_piece_of_data_to_fill), "red")
                await self.send_available_client_actions(self.get_available_client_actions("blue", current_game_action_container, next_piece_of_data_to_fill), "blue")
                await current_game_action_container.event.wait()

    async def execute_place_shape_on_tile_action(self, player_color, slot_index, tile_index, shape_type):
        if self.game_state["whose_turn_is_it"] != player_color:
            await self.send_clients_new_log_message("Not your turn")
            return

        tile = self.game_state["tiles"][tile_index]
        slot = tile.slots_for_shapes[slot_index]

        if slot and game_constants.shape_hierarchy[shape_type] <= game_constants.shape_hierarchy[slot['shape']]:
            await self.send_log_message("Cannot place on this slot, shape is too weak")
            return

        if self.game_state["shapes_in_storage"][player_color][shape_type] <= 0:
            await self.send_log_message(f"No {shape_type}s in storage")
            return

        self.game_state["shapes_in_storage"][player_color][shape_type] -= 1

        await game_engine_utilities.place_shape_on_tile(self.game_state, tile_index, slot_index, shape_type, player_color, self.send_clients_new_log_message)

        game_engine_utilities.determine_rulers(self.game_state)

        if self.game_state["player_has_passed"][game_engine_utilities.determine_rulers(player_color)] == False:
            self.game_state["whose_turn_is_it"] = game_engine_utilities.determine_rulers(player_color)
            self.game_state["whose_action_is_it"] = game_engine_utilities.determine_rulers(player_color)

            await self.send_log_message(f"Turn passes to {self.game_state['whose_turn_is_it']} player")
        else:
            await self.send_log_message(f"{game_engine_utilities.determine_rulers(player_color)} has passed, turn remains with {player_color}")

        await self.send_updated_game_state()

    async def execute_game_action(self, game_action_container):

        match game_action_container.game_action:
            case 'use_tile':
                tile = self.game_state["tiles"][game_action_container.required_data_for_action["index_of_tile_in_use"]]
                # if use tile returns false, the action failed, so don't update the rest of the game state
                if not await tile.use_tile(self.game_state, game_action_container.whose_action, self.send_clients_new_log_message, **game_action_container.required_data_for_action):
                    return
            case 'use_powerup':
                powerup = self.game_state["powerups"][game_action_container.whose_action][game_action_container.required_data_for_action["index_of_powerup_in_use"]]
                # if use powerup returns false, the action failed, so don't update the rest of the game state
                if not await powerup.use_powerup(self.game_state, game_action_container.whose_action, self.send_clients_new_log_message, **game_action_container.required_data_for_action):
                    return
            case 'place_shape_on_tile_slot':

                tile_index = self.game_action_container.required_data_for_action["tile_slot_to_place_on"]["tile_index"]
                slot_index = self.game_action_container.required_data_for_action["tile_slot_to_place_on"]["slot_index"]
                await self.execute_place_shape_on_tile_action(game_action_container.whose_action, slot_index, tile_index, game_action_container.required_data_for_action["shape_type_to_place"])
            case 'pass':
                pass

    def process_data_from_client(self, data, player_color):
        current_game_action_container = self.game_action_container_stack[-1]

        if current_game_action_container.whose_action != player_color:
            self.send_clients_new_log_message(f"{player_color} tried to take action but it's not their action to take")
            return
        
        if current_game_action_container.game_action == "initial_decision":
            #we're processing an initial decision, so we're pop off the "make decision" game action container and replace it below with 
            #an actual game action based on whatever the client chose
            self.game_action_container_stack.pop()
            match data.client_action:
                case 'pass':
                    new_game_action_container = game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="pass",
                                    required_data_for_action={},
                                    whose_action=self.game_state.whose_turn_is_it
                                )

                case 'select_a_shape_in_storage':
                    new_game_action_container = game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="place_shape_on_tile_slot",
                                    required_data_for_action={"shape_type_to_place": data.selected_shape_type_in_storage, "tile_slot_to_place_on": {}},
                                    whose_action=self.game_state.whose_turn_is_it
                                )
                   
                case 'select_a_tile':
                    new_game_action_container = game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="use_tile",
                                    required_data_for_action=OrderedDict(),
                                    whose_action=self.game_state.whose_turn_is_it)
                    
                    new_game_action_container.required_data_for_action["index_of_tile_in_use"] = data.selected_tile_index
                    tile_in_use = self.game_state["tiles"][data.selected_tile_index]
                    for piece_of_data_needed_for_tile_use in tile_in_use.data_needed_for_use:
                        if 'slot' in piece_of_data_needed_for_tile_use:
                            new_game_action_container.required_data_for_action[piece_of_data_needed_for_tile_use] = {}
                        else:
                            new_game_action_container.required_data_for_action[piece_of_data_needed_for_tile_use] = None                

                case 'select_a_powerup':
                    new_game_action_container = game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="use_powerup",
                                    required_data_for_action=OrderedDict(),
                                    whose_action=self.game_state.whose_turn_is_it)
                    
                    new_game_action_container.required_data_for_action["index_of_powerup_in_use"] = data.selected_powerup_index
                    powerup_in_use = self.game_state["powerups"][self.game_state.whose_turn_is_it][data.selected_powerup_index]
                    for piece_of_data_needed_for_powerup_use in powerup_in_use.data_needed_for_use:
                        if 'slot' in piece_of_data_needed_for_powerup_use:
                            new_game_action_container.required_data_for_action[piece_of_data_needed_for_powerup_use] = {}
                        else:
                            new_game_action_container.required_data_for_action[piece_of_data_needed_for_powerup_use] = None

                case _:
                    self.send_clients_new_log_message(f"{player_color} tried to take action but it's not their action to take")
                    return

            self.game_action_container_stack.append(new_game_action_container) 

        else:
            #this data is part of some ongoing action, so we just update the data for it 
            current_game_action_container.required_data_for_action[current_game_action_container.current_piece_of_data_to_fill] = data.data_for_action

        current_game_action_container.event.set() 

    def player_takes_use_powerup_action(local_game_state, powerup_index, player_color, **current_action):
        pass

    def get_available_client_actions(self, player_color, game_action_container, next_piece_of_data_to_fill):

        whose_turn_is_it = self.game_state["whose_turn_is_it"]
        if whose_turn_is_it != player_color:
            return {}
        
        available_client_actions = {"pass": []}

        if game_action_container.game_action == 'place_shape_on_tile_slot':
            shape_type_to_place = game_action_container.data_needed_for_use["shape_type_to_place"]
            slots_that_can_be_placed_on = game_utilities.get_slots_that_can_be_placed_on(self.game_state, shape_type_to_place)
            available_client_actions["select_a_slot_on_a_tile"] = slots_that_can_be_placed_on

        elif game_action_container.game_action == 'use_tile':
            index_of_tile_in_use = game_action_container.data_needed_for_use["index_of_tile_in_use"]
            tile_in_use = self.game_state["tiles"][index_of_tile_in_use]
            tile_in_use.set_available_client_actions(self.game_state, game_action_container, next_piece_of_data_to_fill, available_client_actions)

        elif game_action_container.game_action.game_action == "use_powerup":
            index_of_powerup_in_use = game_action_container.data_needed_for_use["index_of_powerup_in_use"]
            powerup_in_use = self.game_state["powerups"][whose_turn_is_it][index_of_powerup_in_use]
            powerup_in_use.set_available_client_actions(self.game_state, game_action_container, next_piece_of_data_to_fill, available_client_actions)        

        #must be new_turn_choice
        else:
            available_client_actions['select_a_shape_in_storage'] = []
            available_client_actions['select_a_tile'] = []
            available_client_actions['select_a_powerup'] = []

            for shape, amount in self.game_state["shapes_in_storage"][whose_turn_is_it].items():
                if amount > 0:
                    available_client_actions["select_a_shape_in_storage"].append(shape)

            for tile_index, tile in enumerate(self.game_state["tiles"]):
                if tile.is_useable(self.game_state):
                    available_client_actions['select_a_tile'].append(tile_index)
        
            for powerup_index, powerup in enumerate(self.game_state["powerups"]):
                if powerup.is_useable(self.game_state):
                    available_client_actions['select_a_powerup'].append(powerup_index)

        return available_client_actions

    async def perform_conversions(self, local_game_state, player_color, conversions):
        if local_game_state["whose_action_is_it"] != player_color:
            await self.send_log_message(f"It's not {player_color}'s action.")
            return

        for conversion in conversions:
                match conversion:
                    case "circle to square":
                        if local_game_state["shapes_in_storage"][player_color]["circle"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["circle"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.send_log_message(f"{player_color} converts 3 circles to a square")
                        else:
                            await self.send_log_message(f"{player_color} tries to convert 3 circles to a square but doesn't have enough circles")
                    case "square to triangle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["triangle"] += 1
                            await self.send_log_message(f"{player_color} converts 3 squares to a triangle")
                        else:
                            await self.send_log_message(f"{player_color} tries to convert 3 squares to a triangle but doesn't have enough squares")

                    case "triangle to square":
                        if local_game_state["shapes_in_storage"][player_color]["triangle"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["triangle"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.send_log_message(f"{player_color} converts 1 triangle to a square")
                        else:
                            await self.send_log_message(f"{player_color} tries to convert a triangle to a square but doesn't have enough triangles")

                    case "square to circle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["circle"] += 1
                            await self.send_log_message(f"{player_color} converts 1 square to 1 circle")
                        else:
                            await self.send_log_message(f"{player_color} tries to convert a square to a circle but doesn't have enough squares")

    async def start_round(self, self.game_state):
        await self.send_log_message("Starting new round")

        round = self.game_state["round"] 
        if (round > 0):
            self.game_state["round_bonuses"][round-1].cleanup(self.game_state)
        self.game_state["round_bonuses"][round].setup(self.game_state)

        if self.game_state['first_player']:
            self.game_state['whose_turn_is_it'] = self.game_state['first_player']
            self.game_state["whose_action_is_it"] = self.game_state['first_player']
        else:
            self.game_state['whose_turn_is_it'] = 'red'           
        self.game_state['first_player'] = None
        self.game_state['player_has_passed']['red'] = False
        self.game_state['player_has_passed']['blue'] = False
        for tile in self.game_state["tiles"]:
            await tile.start_of_round_effect(self.game_state, self.send_log_message)
            tile.is_on_cooldown = False

        #give base income
        await self.give_base_income_to_players(self.game_state)
        game_engine_utilities.determine_rulers(self.game_state)

    async def give_base_income_to_players(self, self.game_state):
        await self.send_log_message("Giving base income")
        for player_color in game_constants.player_colors:
            for shape, amount in game_constants.shapes_to_give:
                await game_utilities.produce_shape_for_player(self.game_state, player_color, amount, shape, None)

    async def player_takes_use_tile_action(self, self.game_state, tile_index, player_color, **data):

        if self.game_state["whose_turn_is_it"] != player_color:
            await self.send_log_message("Not your turn")
            return
        
        tile = self.game_state["tiles"][tile_index]
        # if use tile returns false, the action failed, so don't update the rest of the game state
        if not await tile.use_tile(self.game_state, player_color, self.send_log_message, **data):
            return
        game_engine_utilities.determine_rulers(self.game_state)
        if self.game_state["player_has_passed"][game_engine_utilities.determine_rulers(player_color)] == False:
            self.game_state["whose_turn_is_it"] = game_engine_utilities.determine_rulers(player_color)
            self.game_state["whose_action_is_it"] = game_engine_utilities.determine_rulers(player_color)
            await self.send_log_message(f"Turn passes to {self.game_state['whose_turn_is_it']} player")
        else:
            await self.send_log_message(f"{game_engine_utilities.determine_rulers(player_color)} has passed, turn remains with {player_color}")

        await self.send_updated_game_state()

    async def player_takes_place_on_slot_on_tile_action(self, self.game_state, player_color, slot_index, tile_index, shape_type):
        if self.game_state["whose_turn_is_it"] != player_color:
            await self.send_log_message("Not your turn")
            return

        tile = self.game_state["tiles"][tile_index]
        slot = tile.slots_for_shapes[slot_index]

        if slot and game_constants.shape_hierarchy[shape_type] <= game_constants.shape_hierarchy[slot['shape']]:
            await self.send_log_message("Cannot place on this slot")
            return

        if self.game_state["shapes_in_storage"][player_color][shape_type] <= 0:
            await self.send_log_message(f"No {shape_type}s in storage")
            return

        self.game_state["shapes_in_storage"][player_color][shape_type] -= 1

        await game_engine_utilities.place_shape_on_tile(self.game_state, tile_index, slot_index, shape_type, player_color, self.send_log_message)

        game_engine_utilities.determine_rulers(self.game_state)

        if self.game_state["player_has_passed"][game_engine_utilities.determine_rulers(player_color)] == False:
            self.game_state["whose_turn_is_it"] = game_engine_utilities.determine_rulers(player_color)
            self.game_state["whose_action_is_it"] = game_engine_utilities.determine_rulers(player_color)

            await self.send_log_message(f"Turn passes to {self.game_state['whose_turn_is_it']} player")
        else:
            await self.send_log_message(f"{game_engine_utilities.determine_rulers(player_color)} has passed, turn remains with {player_color}")

        await self.send_updated_game_state()

    async def player_passes(self, self.game_state, player_color):
        if self.game_state["whose_turn_is_it"] != player_color:
            await self.send_log_message("Not your turn")
            return
        
        await self.send_log_message(f"{player_color} passes")
        self.game_state["player_has_passed"][player_color] = True

        if self.game_state["player_has_passed"][game_engine_utilities.determine_rulers(player_color)] == False:
            await self.send_log_message(f"{player_color} is first player to pass this round and becomes first player")
            self.game_state["first_player"] = player_color

        if self.game_state["player_has_passed"]["red"] and self.game_state["player_has_passed"]["blue"]:
            await self.end_round(self.game_state)

        else:
            self.game_state["whose_turn_is_it"] = game_engine_utilities.determine_rulers(player_color)
            self.game_state["whose_action_is_it"] = game_engine_utilities.determine_rulers(player_color)
            await self.send_log_message(f"turn passes to {self.game_state['whose_turn_is_it']}")

        await self.send_updated_game_state()

    async def end_round(self, self.game_state):
        await self.send_log_message(f"both players have passed, ending round")

        for tile in self.game_state["tiles"]:
            await tile.end_of_round_effect(self.game_state, self.send_log_message)

        for listener_name, listener_function in self.game_state["listeners"]["end_of_round"].items():
            await listener_function(self.game_state, self.send_log_message)  

        game_engine_utilities.determine_rulers(self.game_state)

        if not await self.check_for_end_of_game(self.game_state):
            self.game_state["round"] += 1
            await self.start_round(self.game_state)

    async def check_for_end_of_game(self, self.game_state):
        await self.send_log_message(f"checking for end of game")
        tiles_with_a_ruler = [tile for tile in self.game_state["tiles"] if tile.determine_ruler(self.game_state) is not None]
        if len(tiles_with_a_ruler) >= 7:
           await self.send_log_message(f"7 or more tiles have a ruler, ending game")
           await self.end_game(self.game_state)
           return True
        if (self.game_state["round"] == 5):
            await self.send_log_message(f"Round 5, ending game")
            await self.end_game(self.game_state)
            return True
        
        return False

    async def end_game(self, self.game_state):
        for tile in self.game_state["tiles"]:
            await tile.end_of_game_effect(self.game_state, self.send_log_message)

        await self.send_updated_game_state()
        await self.send_log_message(f"Final Score: Red: {self.game_state['points']['red']} Blue: {self.game_state['points']['blue']}")

        if self.game_state["points"]["red"] > self.game_state["points"]["blue"]:
            await self.send_log_message("Red wins!")
        elif self.game_state["points"]["blue"] > self.game_state["points"]["red"]:
            await self.send_log_message("Blue wins!")
        else:
            await self.send_log_message("It's a tie!")
