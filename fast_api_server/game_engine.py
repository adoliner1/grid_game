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
import round_bonuses
from tiles.tile import Tile

class GameEngine:

    def __init__(self):
        self.game_state = self.create_new_game_state()
        self.send_clients_log_message = None
        self.send_clients_game_state = None
        self.send_available_actions = None
        self.listeners = {"on_place": {}, "start_of_round": {}, "end_of_round": {}, "on_produce": {}}
        self.game_has_ended = False
        self.game_action_container_stack: List[game_action_container.GameActionContainer] = []
        self.game_action_container_stack.append(self.create_initial_decision_game_action_container())
        self.round_just_ended = False

    def set_websocket_callbacks(self, send_clients_log_message, send_clients_game_state, send_clients_available_actions):
        self.send_clients_log_message = send_clients_log_message
        self.send_clients_game_state = send_clients_game_state
        self.send_available_actions = send_clients_available_actions

    async def start_game(self):
        await self.start_round()
        await self.perform_initial_placements()
        await self.run_game_loop()

    async def perform_initial_placements(self):
        await self.send_clients_log_message(f"players must make their initial placements")  
        await self.send_clients_game_state(self.game_state)
        for number_of_initial_circles_placed in range(4):
            player = 'red' if number_of_initial_circles_placed % 2 == 0 else 'blue'
            await self.send_clients_log_message(f"{player} must place a circle")            
            action = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="initial_circle_placement",
                required_data_for_action={
                    'tile_slot_to_place_on': {}
                },
                whose_action=player
            )

            self.game_action_container_stack.append(action)
            await self.get_and_send_available_actions()
            await self.game_action_container_stack[-1].event.wait()
            await self.send_clients_game_state(self.game_state)

        for player in game_constants.player_colors:
            await self.send_clients_log_message(f"{player} must place their leader")
            action = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="initial_leader_placement",
                required_data_for_action={
                    'tile_index_to_place_on': {}
                },
                whose_action=player
            )

            self.game_action_container_stack.append(action)
            await self.get_and_send_available_actions()
            await self.game_action_container_stack[-1].event.wait()  
            await self.send_clients_game_state(self.game_state)    

    async def get_and_send_available_actions(self):
        top_of_game_action_stack = self.game_action_container_stack[-1]
        for player in game_constants.player_colors:
            await self.send_available_actions(game_utilities.get_available_client_actions(self.game_state, top_of_game_action_stack, player_color_to_get_actions_for=player),
                                              top_of_game_action_stack.get_next_piece_of_data_to_fill(),
                                              player)

    #whenever we're in this loop, it means an initial (turn starting) decision needs to be made
    async def run_game_loop(self):
        while not self.game_has_ended:
            #outside of the initial game_state, the stack will always be empty here. when we're here, it indicates a turn just finished, so we need to figure out who goes next\
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

            await self.send_clients_game_state(self.game_state)
            await self.get_and_send_available_actions()
            await self.game_action_container_stack[-1].event.wait()

    #populates the data in the action at the top of the stack with the decision from the client
    #executes the action if it's ready and sends new available actions otherwise
    async def process_data_from_client(self, data, player_color):
        if self.game_action_container_stack[-1].whose_action != player_color:
            await self.send_clients_log_message(f"{player_color} tried to take action but it's not their action to take")
            return

        if data['client_action'] == "do_not_react":    
            if not self.game_action_container_stack[-1].is_a_reaction:
                await self.send_clients_log_message(f"{player_color} chose not to react but it's not a reaction on top of the stack")
            else:
                await self.send_clients_log_message(f"{player_color} chooses not to react")

                action_to_not_react_with = self.game_action_container_stack.pop()
                reactions_to_resolve_container = self.game_action_container_stack[-1]
                #remove that tile from the reactions to resolve, a tile can only be reacted with once per event
                reactions_to_resolve_container.tiers_to_resolve.pop(action_to_not_react_with.required_data_for_action['index_of_tile_in_use'])
                #reset the required data field
                reactions_to_resolve_container.required_data_for_action['tier_to_react_with'] = {}
                action_to_not_react_with.event.set()
                return

        if data['client_action'] == "reset_current_action":
            #only have initial decision container - do nothing
            if len(self.game_action_container_stack) < 2:
                return
            #can't remove a reaction - reset the resettable data in it. then resend available actions.
            elif self.game_action_container_stack[-1].is_a_reaction:
                await self.send_clients_log_message(f"Resetting current action")
                self.reset_resettable_values(self.game_action_container_stack[-1].required_data_for_action)
                self.get_and_send_available_actions()
            #game action pushed from an initial decision, we can just remove it entirely and then resend available actions for the initial decision
            else:
                await self.send_clients_log_message(f"Resetting current action")
                self.game_action_container_stack.pop()
                await self.get_and_send_available_actions()
            return

        if self.game_action_container_stack[-1].game_action == "initial_circle_placement":
            await game_utilities.place_shape_on_tile(self.game_state,
                                              self.game_action_container_stack,
                                                self.send_clients_log_message,
                                                  self.get_and_send_available_actions,
                                                    self.send_clients_game_state, 
                                                     data['tile_slot_to_place_on']['tile_index'],
                                                       data['tile_slot_to_place_on']['slot_index'],
                                                         'circle',
                                                           player_color)
            
            self.game_action_container_stack.pop().event.set()
            await self.send_clients_game_state(self.game_state)            
            return
        
        elif self.game_action_container_stack[-1].game_action == "initial_leader_placement":
            await game_utilities.place_leader_on_tile(self.game_state,
                                              self.game_action_container_stack,
                                                self.send_clients_log_message,
                                                  self.get_and_send_available_actions,
                                                    self.send_clients_game_state, 
                                                     data['tile_index_to_place_on'],
                                                        player_color)
            
            self.game_action_container_stack.pop().event.set()
            await self.send_clients_game_state(self.game_state)            
            return
            
        elif self.game_action_container_stack[-1].game_action == "initial_decision":
            new_game_action_container = self.create_new_game_action_container_from_initial_decision(data)
            if new_game_action_container:
                self.game_action_container_stack.append(new_game_action_container)
            else:
                await self.send_clients_log_message(f"{player_color} sent an invalid client action")
                return
            
        elif self.game_action_container_stack[-1].game_action == "choose_a_reaction_to_resolve":
            tile_index = data['tier_to_react_with']['tile_index']
            tier_index = data['tier_to_react_with']['tier_index']
            await self.game_state['tiles'][tile_index].create_append_and_send_available_actions_for_container(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state, tier_index)            
            
            reactions_to_resolve_container = self.game_action_container_stack[-1]
            #nothing more to resolve. we can pop it and set it
            if not reactions_to_resolve_container.tiers_to_resolve:
                self.game_action_container_stack.pop().event.set()
                #need to return here to stop the task that was handling the resolution of reactions. It no longer has any more game containers to add to the stack
                #so it would erroneously execute the action that spawned the reactions again if we were to let it keep running
                return

        #should be ongoing use a tier
        else:
            data_key = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
            self.game_action_container_stack[-1].required_data_for_action[data_key] = data[data_key]

        #figure out if we need to have the client make another decision, or if we're ready to execute the action.
        #execute it if we're ready. If it was a reaction, we need to remove that tile from the reactions to resolve and reset the tier to react with in case there are more

        next_piece_of_data_to_fill = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
        if not next_piece_of_data_to_fill:
            action_to_execute = self.game_action_container_stack[-1]
            await self.execute_game_action(action_to_execute)
            if action_to_execute.is_a_reaction:
                #the reaction just got popped and executed, the container that was under it should be the reactions to resolve container
                reactions_to_resolve_container = self.game_action_container_stack[-1]
                #remove that tile from the reactions to resolve, a tile can only be reacted with once per event
                reactions_to_resolve_container.tiers_to_resolve.pop(action_to_execute.required_data_for_action['index_of_tile_in_use'])
                #reset the required data field
                reactions_to_resolve_container.required_data_for_action['tier_to_react_with'] = {}
                action_to_execute.event.set()
            else:
                self.game_action_container_stack.pop().event.set() #this is the old initial decision container. pop it off (we'll make a new one in the main loop).

        else:
            await self.get_and_send_available_actions()

    #only ever executing top of stack.. don't need to pass container?
    async def execute_game_action(self, game_action_container):
        match game_action_container.game_action:
            case 'use_a_tier':
                tile = self.game_state["tiles"][game_action_container.required_data_for_action["index_of_tile_in_use"]]
                tier_index = game_action_container.required_data_for_action["index_of_tier_in_use"]
                # if use tile returns false, the action failed, so don't update the rest of the game state
                if not await tile.use_a_tier(self.game_state, tier_index, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state):
                    return False
            case 'pass':
                if not await self.player_passes(game_action_container.whose_action):
                    return False

        #if we fail before here... we need to reset some data in required data i think
        self.game_action_container_stack.pop()
        await self.send_clients_game_state(self.game_state)
        return True

    def create_new_game_action_container_from_initial_decision(self, data):
        match data['client_action']:
            case 'pass':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="pass",
                    required_data_for_action={},
                    whose_action=self.game_state['whose_turn_is_it']
                )

            case 'select_a_tier':
                tile_index = data['initial_data_passed_along_with_choice']['tile_index']
                tier_index = data['initial_data_passed_along_with_choice']['tier_index']
                required_data = OrderedDict({"index_of_tile_in_use": tile_index, "index_of_tier_in_use": tier_index})
                tile_in_use = self.game_state["tiles"][tile_index]
                tier_in_use = tile_in_use.power_tiers[tier_index]
                if tier_in_use['data_needed_for_use']:
                    for piece_of_data_needed_for_tile_use in tier_in_use['data_needed_for_use']:
                        required_data[piece_of_data_needed_for_tile_use] = {} if 'slot' in piece_of_data_needed_for_tile_use else None
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="use_a_tier",
                    required_data_for_action=required_data,
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case _:
                return None

    def reset_resettable_values(self, data):
        for key, value in data.items():
            if "resettable" in key:
                if isinstance(value, dict):
                    data[key] = {}
                else:
                    data[key] = None
        return data
        
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

    def create_new_game_state(self):
        chosen_tiles = random.sample(self.import_all_tiles_from_folder('tiles'), 9)
        all_bonuses = self.get_all_round_bonuses()
        num_bonuses = min(6, len(all_bonuses))
        chosen_round_bonuses = random.sample(all_bonuses, num_bonuses)
        chosen_round_bonuses = [bonus() for bonus in chosen_round_bonuses]

        game_state = {
            "round": 0,
            "points": {
                "red": 0,
                "blue": 0
            },
            "presence": {
                "red": 0,
                "blue": 0
            },
            "peak_power":{
                "red": 0,
                "blue": 0
            },
            "player_has_passed": {
                "red": False,
                "blue": False
            },
            "stamina": {
                "red": 3,
                "blue": 3
            },
            "location_of_leaders" :{
                "red": None,
                "blue": None,                
            },
            "tiles": [tile() for tile in chosen_tiles],
            "whose_turn_is_it": "red",
            "first_player": "red",
            "round_bonuses": chosen_round_bonuses,
            "listeners": {"on_place": {}, "start_of_round": {}, "end_of_round": {}, "end_game": {}, "on_produce": {}, "on_move": {}, "on_burn": {}, "on_receive": {}},
        }

        for tile in game_state["tiles"]:
            if hasattr(tile, 'setup_listener'):
                tile.setup_listener(game_state)

        return game_state

    def create_initial_decision_game_action_container(self):
        return game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="initial_decision",
                required_data_for_action={"initial_data_passed_along_with_choice": None},
                whose_action="red",
            )

    async def start_round(self):
        await self.send_clients_log_message("Starting new round")
        round = self.game_state["round"] 
        if (round > 0):
            self.game_state["round_bonuses"][round-1].cleanup(self.game_state)
        self.game_state["round_bonuses"][round].setup(self.game_state)         
        self.game_state['player_has_passed']['red'] = False
        self.game_state['player_has_passed']['blue'] = False
        for tile in self.game_state["tiles"]:
            await tile.start_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)
            for tier in tile.power_tiers:
                tier['is_on_cooldown'] = False

        for _, listener_function in self.game_state["listeners"]["start_of_round"].items():
                await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)  

        game_utilities.determine_rulers(self.game_state)

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
            await tile.end_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)

        for _, listener_function in self.game_state["listeners"]["end_of_round"].items():
            await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)  

        game_utilities.determine_rulers(self.game_state)

        #not normally to do this here
        await self.send_clients_game_state(self.game_state)

        if not await self.check_for_end_of_game():
            self.game_state["round"] += 1
            await self.start_round()

    async def check_for_end_of_game(self):
        await self.send_clients_log_message(f"checking for end of game")
        tiles_with_a_ruler = [tile for tile in self.game_state["tiles"] if tile.determine_ruler(self.game_state) is not None]
        if len(tiles_with_a_ruler) == 9:
            await self.send_clients_log_message(f"All tiles have a ruler, ending game")
            await self.end_game()
            return True
        if (self.game_state["round"] == 5):
            await self.send_clients_log_message(f"Round 5, ending game")
            await self.end_game()
            return True
        
        return False

    async def end_game(self):
        for tile in self.game_state["tiles"]:
            await tile.end_of_game_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)

        for _, listener_function in self.game_state["listeners"]["end_game"].items():
            await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)  

        await self.send_clients_game_state(self.game_state)
        await self.send_clients_log_message(f"Final Score: Red: {self.game_state['points']['red']} Blue: {self.game_state['points']['blue']}")

        if self.game_state["points"]["red"] > self.game_state["points"]["blue"]:
            await self.send_clients_log_message("Red wins!")
        elif self.game_state["points"]["blue"] > self.game_state["points"]["red"]:
            await self.send_clients_log_message("Blue wins!")
        else:
            await self.send_clients_log_message("It's a tie!")

        self.game_has_ended = True