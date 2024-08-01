import importlib
import inspect
import os
import random
import sys
from typing import Callable, List, OrderedDict
import game_utilities
import game_constants
import game_action_container
import asyncio
import powerups
import round_bonuses
from tiles.tile import Tile

class GameEngine:

    def __init__(self):
        self.game_state = self.create_new_game_state()
        self.send_clients_log_message = None
        self.send_clients_game_state = None
        self.send_clients_available_actions = None
        self.listeners = {"on_place": {}, "start_of_round": {}, "end_of_round": {}, "on_produce": {}}
        self.game_has_ended = False
        self.game_action_container_stack: List[game_action_container.GameActionContainer] = []
        self.game_action_container_stack.append(self.create_initial_decision_game_action_container())
        self.round_just_ended = False
        self.action_queue = asyncio.Queue()
        self.processing_task = None

    def set_websocket_callbacks(self, send_clients_log_message, send_clients_game_state, send_clients_available_actions):
        self.send_clients_log_message = send_clients_log_message
        self.send_clients_game_state = send_clients_game_state
        self.send_clients_available_actions = send_clients_available_actions

    async def start_game(self):
        await self.start_round()
        self.processing_task = asyncio.create_task(self.process_actions())
        await self.run_game_loop()

    #whenever we're in this loop, it means an initial (turn starting) decision needs to be made
    async def run_game_loop(self):
        while not self.game_has_ended:
            #outside of the initial game_state, the stack will always be empty here. when we're here, it indicates a turn just finished, so we need to figure out who goes next
            if not self.game_action_container_stack:
                self.game_action_container_stack.append(self.create_initial_decision_game_action_container())

                if self.round_just_ended:
                    await self.send_clients_log_message(f"New round starting, first player is {self.game_state['first_player']}")
                    self.game_state["whose_turn_is_it"] = self.game_state["first_player"]
                    self.game_action_container_stack[-1].whose_action = self.game_state["whose_turn_is_it"]
                    self.round_just_ended = False
                else:
                    other_player_color = game_utilities.get_other_player_color(self.game_state["whose_turn_is_it"])
                    if self.game_state["player_has_passed"][other_player_color] == False:
                        self.game_state["whose_turn_is_it"] = other_player_color
                        self.game_action_container_stack[-1].whose_action = self.game_state["whose_turn_is_it"]
                        await self.send_clients_log_message(f"Turn passes to {self.game_state['whose_turn_is_it']} player")
                    else:
                        await self.send_clients_log_message(f"{other_player_color} has passed, turn remains with {self.game_state['whose_turn_is_it']}")
                        self.game_action_container_stack[-1].whose_action = self.game_state["whose_turn_is_it"]

            initial_game_action = self.game_action_container_stack[-1]
            await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, initial_game_action, player_color_to_get_actions_for="red"), initial_game_action.get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
            await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, initial_game_action, player_color_to_get_actions_for="blue"), initial_game_action.get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
            await initial_game_action.event.wait()

    def create_new_game_action_container_from_initial_decision(self, data):
        match data['client_action']:
            case 'pass':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="pass",
                    required_data_for_action={},
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case 'select_a_shape_in_storage':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="place_shape_on_tile_slot",
                    required_data_for_action={
                        "shape_type_to_place": data['initial_data_passed_along_with_choice'],
                        "tile_slot_to_place_on": {}
                    },
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case 'select_a_tile':
                required_data = OrderedDict({"index_of_tile_in_use": data['initial_data_passed_along_with_choice']})
                tile_in_use = self.game_state["tiles"][data['initial_data_passed_along_with_choice']]
                for piece_of_data_needed_for_tile_use in tile_in_use.data_needed_for_use:
                    required_data[piece_of_data_needed_for_tile_use] = {} if 'slot' in piece_of_data_needed_for_tile_use else None
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="use_tile",
                    required_data_for_action=required_data,
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case 'select_a_powerup':
                required_data = OrderedDict({"index_of_powerup_in_use": data['initial_data_passed_along_with_choice']})
                powerup_in_use = self.game_state["powerups"][self.game_state['whose_turn_is_it']][data['initial_data_passed_along_with_choice']]
                for piece_of_data_needed_for_powerup_use in powerup_in_use.data_needed_for_use:
                    required_data[piece_of_data_needed_for_powerup_use] = {} if 'slot' in piece_of_data_needed_for_powerup_use else None
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="use_powerup",
                    required_data_for_action=required_data,
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case _:
                return None

    def print_running_tasks(self):
        loop = asyncio.get_running_loop()
        tasks = asyncio.all_tasks(loop)
        print(f"Number of running tasks: {len(tasks)}")

    def reset_resettable_values(self, data):
        for key, value in data.items():
            if "resettable" in key:
                if isinstance(value, dict):
                    data[key] = {}
                else:
                    data[key] = None
        return data

    async def process_actions(self):
        while True:
            action_data = await self.action_queue.get()
            asyncio.create_task(self.process_action(action_data))
            self.action_queue.task_done()

    async def process_action(self, action_data):
        data, player_color = action_data
        if self.game_action_container_stack[-1].whose_action != player_color:
                    await self.send_clients_log_message(f"{player_color} tried to take action but it's not their action to take")
                    return
                
        #TODO probably want a new data structure that describes when a piece of data is resettable and has a directive for it
        if data['client_action'] == "reset_current_action":
            #only have initial decision container - do nothing
            if len(self.game_action_container_stack) < 2:
                return
            #can't remove a reaction - reset the resettable data in it. then resend available actions.
            elif self.game_action_container_stack[-1].is_a_reaction:
                await self.send_clients_log_message(f"Restting current action")
                self.reset_resettable_values(self.game_action_container_stack[-1].required_data_for_action)
                await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="red"), self.game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
                await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="blue"), self.game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
            #game action pushed from an initial decision, we can just remove it entirely and then resend available actions for the initial decision
            else:
                await self.send_clients_log_message(f"Restting current action")
                self.game_action_container_stack.pop()
                await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="red"), self.game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
                await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="blue"), self.game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")

        if self.game_action_container_stack[-1].game_action == "initial_decision":
            new_game_action_container = self.create_new_game_action_container_from_initial_decision(data)
            if new_game_action_container:
                self.game_action_container_stack.append(new_game_action_container)
            else:
                await self.send_clients_log_message(f"{player_color} sent an invalid client action")
                return
            
        else:
            data_key = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
            self.game_action_container_stack[-1].required_data_for_action[data_key] = data[data_key]

        next_piece_of_data_to_fill = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
        #print (next_piece_of_data_to_fill)
        if not next_piece_of_data_to_fill:
            action_to_execute = self.game_action_container_stack[-1]
            await self.execute_game_action(action_to_execute)
            #print ("stack after execute")
            #print (self.game_action_container_stack)
            if action_to_execute.is_a_reaction:
                action_to_execute.event.set()
            else:
                self.game_action_container_stack.pop().event.set() #this is the old initial decision container. pop it off (we'll make a new one in the main loop).

        else:
            await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="red"), next_piece_of_data_to_fill, player_color_to_send_to="red")
            await self.send_clients_available_actions(game_utilities.get_available_client_actions(self.game_state, self.game_action_container_stack[-1], player_color_to_get_actions_for="blue"), next_piece_of_data_to_fill, player_color_to_send_to="blue")    
        
    #effectively creates a loop which takes data from the client, populates the data in the action
    #at the top of the stack, executes the action if it's ready and sends new available actions otherwise
    async def process_data_from_client(self, data, player_color):
        await self.action_queue.put((data, player_color))

    def import_all_tiles_from_folder(self, folder_name):
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

    def get_all_round_bonuses(self):
        module_name = 'round_bonuses'
        module = importlib.import_module(module_name)
        
        round_bonus_classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, round_bonuses.RoundBonus) and obj is not round_bonuses.RoundBonus:
                round_bonus_classes.append(obj)
        
        return round_bonus_classes
    
    def get_all_powerups(self):
        module_name = 'powerups'
        module = importlib.import_module(module_name)
        
        powerup_classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, powerups.Powerup) and obj is not powerups.Powerup:
                powerup_classes.append(obj)
        
        return powerup_classes

    def create_new_game_state(self):
        chosen_tiles = random.sample(self.import_all_tiles_from_folder('tiles'), 9)
        chosen_round_bonuses = [random.choice(self.get_all_round_bonuses())() for _ in range(6)]
        blue_chosen_powerups = [random.choice(self.get_all_powerups()) for _ in range(3)]
        red_chosen_powerups = blue_chosen_powerups.copy() 
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
                "blue": False
            },
            "tiles": [tile() for tile in chosen_tiles],
            "whose_turn_is_it": "red",
            "first_player": "red",
            "powerups": {
                "red": [powerup(owner="red") for powerup in red_chosen_powerups],
                "blue": [powerup(owner="blue") for powerup in blue_chosen_powerups]
            },
            "round_bonuses": chosen_round_bonuses,
            "listeners": {"on_place": {}, "on_powerup_place": {}, "start_of_round": {}, "end_of_round": {}, "on_produce": {}, "on_move": {}, "on_burn": {}},
        }

        for tile in game_state["tiles"]:
            if hasattr(tile, 'setup_listener'):
                tile.setup_listener(game_state)

        for powerup in game_state["powerups"]["red"]:
            if hasattr(powerup, 'setup_listener'):
                powerup.setup_listener(game_state)

        for powerup in game_state["powerups"]["blue"]:
            if hasattr(powerup, 'setup_listener'):
                powerup.setup_listener(game_state)

        return game_state

    def create_initial_decision_game_action_container(self):
        return game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="initial_decision",
                required_data_for_action={"initial_data_passed_along_with_choice": None},
                whose_action="red",
            )

    #only ever executing top of stack.. don't need to pass container?
    async def execute_game_action(self, game_action_container):
        match game_action_container.game_action:
            case 'use_tile':
                tile = self.game_state["tiles"][game_action_container.required_data_for_action["index_of_tile_in_use"]]
                # if use tile returns false, the action failed, so don't update the rest of the game state
                if not await tile.use_tile(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state):
                    return False
            case 'use_powerup':
                powerup = self.game_state["powerups"][game_action_container.whose_action][game_action_container.required_data_for_action["index_of_powerup_in_use"]]
                # if use powerup returns false, the action failed, so don't update the rest of the game state
                if not await powerup.use_powerup(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state):
                    return False
            case 'place_shape_on_tile_slot':
                tile_index = game_action_container.required_data_for_action["tile_slot_to_place_on"]["tile_index"]
                slot_index = game_action_container.required_data_for_action["tile_slot_to_place_on"]["slot_index"]
                if not await self.execute_place_shape_on_tile_slot_action(game_action_container, slot_index, tile_index, game_action_container.required_data_for_action["shape_type_to_place"]):
                    return False
            case 'place_shape_on_powerup_slot':
                powerup_index = game_action_container.required_data_for_action["resettable_powerup_slot_to_place_on"]["powerup_index"]
                slot_index = game_action_container.required_data_for_action["resettable_powerup_slot_to_place_on"]["slot_index"]
                if not await self.execute_place_shape_on_powerup_action(game_action_container, slot_index, powerup_index, game_action_container.required_data_for_action["shape_type_to_place"]):
                    return False
            case 'react_with_tile':
                tile = self.game_state["tiles"][game_action_container.required_data_for_action["index_of_tile_in_use"]]
                # if use tile returns false, the action failed, so don't update the rest of the game state
                if not await tile.react(self.game_state, game_action_container.whose_action, self.send_clients_log_message, **game_action_container.required_data_for_action):
                    return False
            case 'react_with_powerup':
                powerup = self.game_state["powerups"][game_action_container.whose_action][game_action_container.required_data_for_action["index_of_powerup_in_use"]]
                # if react with powerup returns false, the action failed, so don't update the rest of the game state
                if not await powerup.react(self.game_state, game_action_container.whose_action, self.send_clients_log_message, **game_action_container.required_data_for_action):
                    return False
            case 'pass':
                if not await self.player_passes(game_action_container.whose_action):
                    return False

        #if we fail before here... we need to reset some data in required data i think

        self.game_action_container_stack.pop()
        await self.send_clients_game_state(self.game_state)
        return True

    async def execute_place_shape_on_tile_slot_action(self, game_action_container, slot_index, tile_index, shape_type):
        color_of_player_placing = game_action_container.whose_action
        if self.game_state["whose_turn_is_it"] != color_of_player_placing:
            await self.send_clients_log_message("Not your turn")
            return False

        tile = self.game_state["tiles"][tile_index]
        slot = tile.slots_for_shapes[slot_index]

        if slot and game_constants.shape_hierarchy[shape_type] <= game_constants.shape_hierarchy[slot['shape']]:
            await self.send_clients_log_message("Cannot place on this slot, shape is too weak to trump")
            return False

        if self.game_state["shapes_in_storage"][color_of_player_placing][shape_type] <= 0:
            await self.send_clients_log_message(f"No {shape_type}s in storage")
            return False

        self.game_state["shapes_in_storage"][color_of_player_placing][shape_type] -= 1

        await game_utilities.place_shape_on_tile(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state, tile_index, slot_index, shape_type, color_of_player_placing)

        game_utilities.determine_rulers(self.game_state)
        return True
    
    async def execute_place_shape_on_powerup_action(self, game_action_container, slot_index, powerup_index, shape_type):
        color_of_player_placing = game_action_container.whose_action

        powerup = self.game_state["powerups"][color_of_player_placing][powerup_index]
        slot = powerup.slots_for_shapes[slot_index]

        if slot and game_constants.shape_hierarchy[shape_type] <= game_constants.shape_hierarchy[slot['shape']]:
            await self.send_clients_log_message("Cannot place on this slot, shape is too weak to trump")
            return False

        await game_utilities.place_shape_on_powerup(self.game_state,
                                                 self.game_action_container_stack,
                                                 self.send_clients_log_message,
                                                 self.send_clients_available_actions,
                                                 self.send_clients_game_state,
                                                 powerup_index, 
                                                 slot_index, 
                                                 shape_type, 
                                                 color_of_player_placing, 
)

        game_utilities.determine_rulers(self.game_state)
        return True

    async def perform_conversions(self, local_game_state, player_color, conversions):
        if local_game_state["whose_action_is_it"] != player_color:
            await self.send_clients_log_message(f"It's not {player_color}'s action.")
            return

        for conversion in conversions:
                match conversion:
                    case "circle to square":
                        if local_game_state["shapes_in_storage"][player_color]["circle"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["circle"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.send_clients_log_message(f"{player_color} converts 3 circles to a square")
                        else:
                            await self.send_clients_log_message(f"{player_color} tries to convert 3 circles to a square but doesn't have enough circles")
                    case "square to triangle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 3:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 3
                            local_game_state["shapes_in_storage"][player_color]["triangle"] += 1
                            await self.send_clients_log_message(f"{player_color} converts 3 squares to a triangle")
                        else:
                            await self.send_clients_log_message(f"{player_color} tries to convert 3 squares to a triangle but doesn't have enough squares")

                    case "triangle to square":
                        if local_game_state["shapes_in_storage"][player_color]["triangle"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["triangle"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["square"] += 1
                            await self.send_clients_log_message(f"{player_color} converts 1 triangle to a square")
                        else:
                            await self.send_clients_log_message(f"{player_color} tries to convert a triangle to a square but doesn't have enough triangles")

                    case "square to circle":
                        if local_game_state["shapes_in_storage"][player_color]["square"] >= 1:
                            local_game_state["shapes_in_storage"][player_color]["square"] -= 1
                            local_game_state["shapes_in_storage"][player_color]["circle"] += 1
                            await self.send_clients_log_message(f"{player_color} converts 1 square to 1 circle")
                        else:
                            await self.send_clients_log_message(f"{player_color} tries to convert a square to a circle but doesn't have enough squares")

    async def start_round(self):
        await self.send_clients_log_message("Starting new round")
        round = self.game_state["round"] 
        if (round > 0):
            self.game_state["round_bonuses"][round-1].cleanup(self.game_state)
        self.game_state["round_bonuses"][round].setup(self.game_state)         
        self.game_state['player_has_passed']['red'] = False
        self.game_state['player_has_passed']['blue'] = False
        for tile in self.game_state["tiles"]:
            await tile.start_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)
            tile.is_on_cooldown = False

        for powerup in self.game_state["powerups"]["red"]:
            await powerup.start_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)

        for powerup in self.game_state["powerups"]["blue"]:
            await powerup.start_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)                    

        #give base income
        await self.give_base_income_to_players()
        game_utilities.determine_rulers(self.game_state)

    async def give_base_income_to_players(self):
        await self.send_clients_log_message("Giving base income")
        for player_color in game_constants.player_colors:
            for shape, amount in game_constants.base_income:
                await game_utilities.produce_shape_for_player(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state, player_color, amount, shape, None)

    async def player_passes(self, player_color):
        if self.game_state["whose_turn_is_it"] != player_color:
            await self.send_clients_log_message("Not your turn")
            return False
        
        await self.send_clients_log_message(f"{player_color} passes")
        self.game_state["player_has_passed"][player_color] = True

        if self.game_state["player_has_passed"][game_utilities.get_other_player_color(player_color)] == False:
            await self.send_clients_log_message(f"{player_color} is first player to pass this round and becomes first player")
            self.game_state["first_player"] = player_color

        if self.game_state["player_has_passed"]["red"] and self.game_state["player_has_passed"]["blue"]:
            await self.end_round()

        return True

    async def end_round(self):
        await self.send_clients_log_message(f"both players have passed, ending round")
        self.round_just_ended = True
        for tile in self.game_state["tiles"]:
            await tile.end_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)

        for powerup in self.game_state["powerups"]["red"]:
                    await powerup.end_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)

        for powerup in self.game_state["powerups"]["blue"]:
            await powerup.end_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)                    

        game_utilities.determine_rulers(self.game_state)

        #not normally to do this here
        await self.send_clients_game_state(self.game_state)

        if not await self.check_for_end_of_game():
            self.game_state["round"] += 1
            await self.start_round()

    async def check_for_end_of_game(self):
        await self.send_clients_log_message(f"checking for end of game")
        tiles_with_a_ruler = [tile for tile in self.game_state["tiles"] if tile.determine_ruler(self.game_state) is not None]
        if len(tiles_with_a_ruler) >= 7:
            await self.send_clients_log_message(f"7 or more tiles have a ruler, ending game")
            await self.end_game(self.game_state)
            return True
        if (self.game_state["round"] == 5):
            await self.send_clients_log_message(f"Round 5, ending game")
            await self.end_game(self.game_state)
            return True
        
        return False

    async def end_game(self):
        for tile in self.game_state["tiles"]:
            await tile.end_of_game_effect(self.game_state, self.send_clients_log_message)

        for powerup in self.game_state["powerups"]["red"]:
                    await powerup.end_of_game_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)

        for powerup in self.game_state["powerups"]["blue"]:
            await powerup.end_of_game_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.send_clients_available_actions, self.send_clients_game_state)                    

        await self.send_clients_game_state()
        await self.send_clients_log_message(f"Final Score: Red: {self.game_state['points']['red']} Blue: {self.game_state['points']['blue']}")

        if self.game_state["points"]["red"] > self.game_state["points"]["blue"]:
            await self.send_clients_log_message("Red wins!")
        elif self.game_state["points"]["blue"] > self.game_state["points"]["red"]:
            await self.send_clients_log_message("Blue wins!")
        else:
            await self.send_clients_log_message("It's a tie!")
