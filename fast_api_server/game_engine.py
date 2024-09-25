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
        self.game_has_ended = False
        self.game_action_container_stack: List[game_action_container.GameActionContainer] = []
        self.game_action_container_stack.append(self.create_initial_decision_game_action_container())
        self.round_just_ended = False

    def set_websocket_callbacks(self, send_clients_log_message, send_clients_game_state, send_clients_available_actions):
        self.send_clients_log_message = send_clients_log_message
        self.send_clients_game_state = send_clients_game_state
        self.send_available_actions = send_clients_available_actions

    async def start_game(self):
        self.game_state['power']['red'] = game_constants.first_player_starting_power
        self.game_state['power']['blue'] = game_constants.second_player_starting_power
        await self.send_clients_log_message(f"Starting a new game. Red starts with {game_constants.first_player_starting_power} power. Blue starts with {game_constants.second_player_starting_power} power")
        await self.perform_initial_placements()
        await self.start_round()
        await self.run_game_loop()

    async def perform_initial_placements(self):
        await self.send_clients_log_message(f"Players must make their initial follower recruitments and then place their leaders")
        await self.send_clients_game_state(self.game_state)

        #set up listeners outside of start round here here in case an initial recruitment triggers one
        for _ , listener_function in self.game_state["listeners"]["start_of_round"].values():
            await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)  

        for number_of_initial_followers_placed in range(game_constants.number_of_initial_followers_to_place):
            player = 'red' if number_of_initial_followers_placed % 2 == 0 else 'blue'
            self.game_state['whose_turn_is_it'] = player
            await self.send_clients_game_state(self.game_state)
            await self.send_clients_log_message(f"{player} must recruit a {player}_follower (they can choose any tile because it's the start of the game)")            
            action = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="initial_follower_placement",
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
            self.game_state['whose_turn_is_it'] = player
            await self.send_clients_game_state(self.game_state)    
            await self.send_clients_log_message(f"{player} must place their {player}_leader")
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

        self.game_state['whose_turn_is_it'] = 'red'
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
            if self.game_action_container_stack[-1].game_action == 'move_leader':
                await self.send_clients_log_message(f"{player_color} chooses not to use the rest of their movement")
                self.game_action_container_stack.pop()
                self.game_action_container_stack.pop().event.set()

            elif not self.game_action_container_stack[-1].is_a_reaction:
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
            cant_reset_conditions = [
                len(self.game_action_container_stack) < 2,
                self.game_action_container_stack[-1].game_action in [
                    'choose_a_reaction_to_resolve',
                    'initial_follower_placement',
                    'initial_leader_placement'
                ],
                self.game_action_container_stack[-1].game_action == 'move_leader' and 
                self.game_action_container_stack[-1].movements_made > 0
            ]

            # Check if any condition preventing reset is true
            if any(cant_reset_conditions):
                await self.send_clients_log_message(f"Can't cancel this action")
                return
            #the action is resettable, we just pop it off and resend the available actions
            else:
                await self.send_clients_log_message(f"Cancelling action")
                self.game_action_container_stack.pop()
                await self.get_and_send_available_actions()
            return

        if self.game_action_container_stack[-1].game_action == "initial_follower_placement":
            await game_utilities.recruit_disciple_on_tile(self.game_state,
                                              self.game_action_container_stack,
                                                self.send_clients_log_message,
                                                  self.get_and_send_available_actions,
                                                    self.send_clients_game_state, 
                                                     data['tile_slot_to_place_on']['tile_index'],
                                                       data['tile_slot_to_place_on']['slot_index'],
                                                         'follower',
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
                #need to return here to stop the task that was handling the resolution of reactions. It no longer has any more game-reaction containers to add to the stack
                #so it would erroneously execute the action that spawned the reactions for a second time if we let it keep running
                return

        #ongoing action that data needs to be added to
        else:
            data_key = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
            self.game_action_container_stack[-1].required_data_for_action[data_key] = data[data_key]

        #figure out if we need to have the client make another decision or if we're ready to execute the action.
        #execute it if we're ready. If it was a reaction, we need to remove that tile from the reactions to resolve and reset the tier to react with in case there are more

        next_piece_of_data_to_fill = self.game_action_container_stack[-1].get_next_piece_of_data_to_fill()
        if not next_piece_of_data_to_fill:
            action_to_execute = self.game_action_container_stack[-1]
            if not await self.execute_game_action(action_to_execute):
                #the action failed for some reason. We just treat it like a reset, we pop it off and resend the available actions based on the container below it
                await self.send_clients_log_message(f"Action failed, resetting")
                self.game_action_container_stack.pop()
                await self.get_and_send_available_actions()
                return
            
            #after an action is successfully executed, we need to pop off the old initial decision container
            #the exception is if we're in the middle of a move_leader action and there are more moves they can make
            else:
                if action_to_execute.game_action != 'move_leader':
                    self.game_action_container_stack.pop().event.set()
                else:
                    if not action_to_execute.movements_made < self.game_state['leader_movement'][action_to_execute.whose_action]:
                        self.game_action_container_stack.pop().event.set()
                        
            if action_to_execute.is_a_reaction:
                #the reaction just got popped and executed, the container that was under it should be the reactions to resolve container
                reactions_to_resolve_container = self.game_action_container_stack[-1]
                #remove that tile from the reactions to resolve, a tile can only be reacted with once per event
                reactions_to_resolve_container.tiers_to_resolve.pop(action_to_execute.required_data_for_action['index_of_tile_in_use'])
                #reset the required data field
                reactions_to_resolve_container.required_data_for_action['tier_to_react_with'] = {}
                action_to_execute.event.set()

        else:
            await self.get_and_send_available_actions()

    #only ever executing top of stack.. don't need to pass container?
    async def execute_game_action(self, game_action_container):
        match game_action_container.game_action:
            case 'use_a_tier':
                tile = self.game_state["tiles"][game_action_container.required_data_for_action["index_of_tile_in_use"]]
                tier_index = game_action_container.required_data_for_action["index_of_tier_in_use"]
                if not await tile.use_a_tier(self.game_state, tier_index, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state):
                    return False
            case 'pass':
                if not await self.player_passes(game_action_container.whose_action):
                    return False
            case 'move_leader':
                if not await self.player_takes_move_leader_action(game_action_container):
                    return False
                
                #if more moves can be done we need to do what we normally do, but not pop off the container yet
                if game_action_container.movements_made < self.game_state['leader_movement'][game_action_container.whose_action]:
                    game_action_container.required_data_for_action['tile_index_to_move_leader_to'] = None
                    game_utilities.determine_influence_levels(self.game_state)
                    game_utilities.update_presence(self.game_state)
                    game_utilities.determine_rulers(self.game_state)
                    game_utilities.calculate_exiling_ranges(self.game_state)
                    game_utilities.calculate_recruiting_ranges(self.game_state)
                    game_utilities.calculate_expected_incomes(self.game_state)
                    await self.send_clients_game_state(self.game_state)
                    await self.get_and_send_available_actions()
                    return True

            case 'exile':
                if not await self.player_takes_exile_action(game_action_container):
                    return False
            case 'recruit':
                if not await self.player_takes_recruit_action(game_action_container):
                    return False

        game_utilities.determine_influence_levels(self.game_state)
        game_utilities.update_presence(self.game_state)
        game_utilities.determine_rulers(self.game_state)
        game_utilities.calculate_exiling_ranges(self.game_state)
        game_utilities.calculate_recruiting_ranges(self.game_state)
        game_utilities.calculate_expected_incomes(self.game_state)
        self.game_action_container_stack.pop()
        await self.send_clients_game_state(self.game_state)
        return True

    async def player_takes_move_leader_action(self, game_action_container):
        mover = game_action_container.whose_action
        tile_index_to_move_leader_to = game_action_container.required_data_for_action['tile_index_to_move_leader_to']
        tile_index_of_players_leader = game_utilities.get_tile_index_of_leader(self.game_state, mover)
        tile_indices_adjacent_to_leader = game_utilities.get_adjacent_tile_indices(tile_index_of_players_leader)
        tile_of_players_leader = self.game_state['tiles'][tile_index_of_players_leader]
        tile_to_move_leader_to = self.game_state['tiles'][tile_index_to_move_leader_to]
        if not tile_index_to_move_leader_to in tile_indices_adjacent_to_leader:
            await self.send_clients_log_message(f"Chose a non-adjacent tile to move leader to")           
            return False
        
        #if it's the first move, we make sure they have enough power and then reduce the power
        if game_action_container.movements_made == 0:
            if self.game_state['power'][mover] < 1:
                await self.send_clients_log_message("Don't have enough power to move leader")
                return False

            self.game_state['power'][mover] -= 1

        await self.send_clients_log_message(f"{mover}_leader moves from **{tile_of_players_leader.name}** to **{tile_to_move_leader_to.name}**")
        game_action_container.movements_made += 1 
        tile_of_players_leader.leaders_here[mover] = False
        tile_to_move_leader_to.leaders_here[mover] = True
        return True
    
    async def player_takes_recruit_action(self, game_action_container):
        tile_index = game_action_container.required_data_for_action["tile_slot_to_recruit_on"]["tile_index"]
        slot_index = game_action_container.required_data_for_action["tile_slot_to_recruit_on"]["slot_index"]
        disciple_type = game_action_container.required_data_for_action["disciple_type_to_recruit"]
        color_of_player_recruiting = game_action_container.whose_action
        tile = self.game_state["tiles"][tile_index]
        slot = tile.slots_for_disciples[slot_index]
        
        if self.game_state["whose_turn_is_it"] != color_of_player_recruiting:
            await self.send_clients_log_message("Not your turn")
            return False

        if tile_index not in game_utilities.get_tiles_within_recruiting_range(self.game_state, disciple_type, game_action_container.whose_action):
            await self.send_clients_log_message("Not in range of that tile")
            return False               

        if disciple_type not in tile.disciples_which_can_be_recruited_to_this:
            await self.send_clients_log_message("Cannot recruit this disciple here")
            return False    

        if slot and not (game_constants.disciple_influence[slot['disciple']] < game_constants.disciple_influence[disciple_type] and color_of_player_recruiting == slot['color']):
            await self.send_clients_log_message("Cannot recruit on this slot, it's not empty or contains one of your weaker disciples")
            return False
        
        if self.game_state['costs_to_recruit'][color_of_player_recruiting][disciple_type] > self.game_state['power'][color_of_player_recruiting]:
            await self.send_clients_log_message("Don't have enough power to recruit this")
            return False
        

        self.game_state['power'][color_of_player_recruiting] -= self.game_state['costs_to_recruit'][color_of_player_recruiting][disciple_type]
        await game_utilities.recruit_disciple_on_tile(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state, tile_index, slot_index, disciple_type, color_of_player_recruiting)
        game_utilities.determine_rulers(self.game_state)
        return True
     
    async def player_takes_exile_action(self, game_action_container):
        tile_index_to_exile_from = game_action_container.required_data_for_action["tile_slot_to_exile_from"]["tile_index"]
        slot_index_to_exile_from = game_action_container.required_data_for_action["tile_slot_to_exile_from"]["slot_index"]
        tile_to_exile_from = self.game_state['tiles'][tile_index_to_exile_from]
        slot_to_exile_from = tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from]
        exiled_color = tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from]['color']
        exiled_disciple = tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from]['disciple']
        color_of_player_exiling = game_action_container.whose_action

        if tile_index_to_exile_from not in game_utilities.get_tiles_within_exiling_range(self.game_state, game_action_container.whose_action):
            await self.send_clients_log_message("Not in range of that tile")
            return False

        if slot_to_exile_from is None:
            await self.send_clients_log_message("Nothing to exile here")
            return False
        
        if self.game_state['costs_to_exile'][color_of_player_exiling][slot_to_exile_from['disciple']] > self.game_state['power'][color_of_player_exiling]:
            await self.send_clients_log_message("Not enough power to exile")
            return False            

        self.game_state['power'][color_of_player_exiling] -= self.game_state['costs_to_exile'][color_of_player_exiling][slot_to_exile_from['disciple']]
        tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from] = None
        await self.send_clients_log_message(f"{color_of_player_exiling} exiled a {exiled_color}_{exiled_disciple} from **{tile_to_exile_from.name}** for {self.game_state['costs_to_exile'][color_of_player_exiling][exiled_disciple]} power")
        return True
    def create_new_game_action_container_from_initial_decision(self, data):
        match data['client_action']:
            case 'move_leader':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="move_leader",
                    required_data_for_action={
                        "tile_index_to_move_leader_to": None
                    },
                    whose_action = self.game_state['whose_turn_is_it'],
                )
            case 'exile':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="exile",
                    required_data_for_action={
                        "tile_slot_to_exile_from": {},
                    },
                    whose_action=self.game_state['whose_turn_is_it']
                )
            case 'recruit':
                return game_action_container.GameActionContainer(
                    event=asyncio.Event(),
                    game_action="recruit",
                    required_data_for_action={
                        "disciple_type_to_recruit": None,
                        "tile_slot_to_recruit_on": {}
                    },
                    whose_action=self.game_state['whose_turn_is_it']
                )

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
                tier_in_use = tile_in_use.influence_tiers[tier_index]
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
       
        scorer_bonuses = []
        income_bonuses = []
       
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, round_bonuses.RoundBonus) and obj is not round_bonuses.RoundBonus:
                if obj().bonus_type == "scorer":
                    scorer_bonuses.append(obj)
                elif obj().bonus_type == "income":
                    income_bonuses.append(obj)
       
        return scorer_bonuses, income_bonuses

    def create_new_game_state(self):
        chosen_tiles = random.sample(self.import_all_tiles_from_folder('tiles'), 9)
        scorer_bonuses, income_bonuses = self.get_all_round_bonuses()  
    
        chosen_scorer_bonuses = random.sample(scorer_bonuses, game_constants.number_of_scoring_bonuses)
        chosen_income_bonuses = random.sample(income_bonuses, game_constants.number_of_income_bonuses)
    
        game_state = {
            "round": 0,
            "points": {"red": 0, "blue": 0},
            "presence": {"red": 0, "blue": 0},
            "peak_influence": {"red": 0, "blue": 0},
            "player_has_passed": {"red": False, "blue": False},
            "power": {"red": 0, "blue": 0},
            "recruiting_range": {"red": 0, "blue": 0},
            "exiling_range": {"red": 0, "blue": 0},
            "expected_power_incomes": {"red": 0, "blue": 0}, #not really part of game state, should be somewhere else
            "expected_points_incomes": {"red": 0, "blue": 0}, #not really part of game state, should be somewhere else
            "costs_to_recruit": {"red": game_constants.starting_cost_to_recruit, "blue": game_constants.starting_cost_to_recruit},
            "costs_to_exile": {"red": game_constants.starting_cost_to_exile, "blue": game_constants.starting_cost_to_exile},
            "power_given_at_start_of_round": game_constants.power_given_at_end_of_round,
            "leader_movement": {"red": game_constants.starting_leader_movement['red'], "blue": game_constants.starting_leader_movement['blue']},
            "tiles": [tile() for tile in chosen_tiles],
            "whose_turn_is_it": "red",
            "first_player": "red",
            "scorer_bonuses": [bonus() for bonus in chosen_scorer_bonuses],
            "income_bonuses": [bonus() for bonus in chosen_income_bonuses],
            "listeners": {
                "on_recruit": {}, "start_of_round": {}, "end_of_round": {}, "end_game": {},
                "on_produce": {}, "on_move": {}, "on_burn": {}, "on_receive": {}
            },
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
        
        if round > 0:
            self.game_state["scorer_bonuses"][round-1].cleanup(self.game_state)
            self.game_state["income_bonuses"][round-1].cleanup(self.game_state)
    
        self.game_state["scorer_bonuses"][round].setup(self.game_state)
        self.game_state["income_bonuses"][round].setup(self.game_state)

        self.game_state['player_has_passed']['red'] = False
        self.game_state['player_has_passed']['blue'] = False
        
        for tile in self.game_state["tiles"]:
            await tile.start_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)
            for tier in tile.influence_tiers:
                tier['is_on_cooldown'] = False
        
        for _ , listener_function in self.game_state["listeners"]["start_of_round"].values():
            await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)      
            game_utilities.determine_rulers(self.game_state)
    
        game_utilities.calculate_expected_incomes(self.game_state)

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
        await self.send_clients_log_message(f"Both players have passed, ending round")
        self.round_just_ended = True
        for tile in self.game_state["tiles"]:
            await tile.end_of_round_effect(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)

        for _, listener_function in self.game_state["listeners"]["end_of_round"].items():
            await listener_function(self.game_state, self.game_action_container_stack, self.send_clients_log_message, self.get_and_send_available_actions, self.send_clients_game_state)  

        game_utilities.determine_rulers(self.game_state)

        #base power-income
        if self.game_state["round"] < 5:
            power_to_give = game_constants.power_given_at_end_of_round[self.game_state["round"]]
            await self.send_clients_log_message(f"Giving {power_to_give} power to each player (base-income)")        
            
            for player in game_constants.player_colors:
                self.game_state['power'][player] += power_to_give

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