import asyncio
import game_action_container
from tile import Tile
import game_utilities
import game_constants

class CircleOfTheCricket(Tile):
    def __init__(self):
        super().__init__(
            name="Circle of the Cricket",
            type="Generator/Giver",
            number_of_slots=2,
            minimum_influence_to_rule=2,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": True,                    
                    "description": "**Action:** [[Receive]] a follower at an adjacent tile. Your opponent gets +1 power",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": ["tile_to_receive_follower"],
                    "has_a_cooldown": True,                    
                },                
            ],      
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        current_player = game_state["whose_turn_is_it"]

        if not self.influence_tiers[0]["is_on_cooldown"] and self.determine_ruler(game_state) == current_player:
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_utilities.find_index_of_tile_by_name(game_state, self.name))
        available_actions["select_a_tile"] = indices_of_adjacent_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
                                                                     
        if not ruler:
            await send_clients_log_message(f"No ruler determined for **{self.name}**, cannot use")
            return False
       
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False

        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown and cannot be used this round")
            return False

        index_of_tile_to_receive_disciples_on = game_action_container.required_data_for_action['tile_to_receive_follower']
        tile_to_receive_disciples_on = game_state['tiles'][index_of_tile_to_receive_disciples_on]
        
        if not game_utilities.determine_if_directly_adjacent(index_of_tile_to_receive_disciples_on, game_utilities.find_index_of_tile_by_name(game_state, self.name)):
            await send_clients_log_message(f"Chose non-adjacent tile while using **{self.name}**")
            return False

        await send_clients_log_message(f"**{self.name}** is used")
        self.influence_tiers[0]['is_on_cooldown'] = True
        await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, ruler, tile_to_receive_disciples_on, 'follower')
        other_player = game_utilities.get_other_player_color(ruler)
        await send_clients_log_message(f"{other_player} gets +1 power")
        game_state['power'][other_player] += 1 
        return True