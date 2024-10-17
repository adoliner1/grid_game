import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class RiftOfDarkness(Tile):
    def __init__(self):
        super().__init__(
            name="Rift of Darkness",
            type="Leader-Movement",
            minimum_influence_to_rule=4,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "**Action:** Teleport your opponent to a tile within 2 tiles of their current location",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False,
                    "data_needed_for_use": ["tile_to_move_leader_to"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
       
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]["is_on_cooldown"] and
            whose_turn_is_it == ruler):
                useable_tiers.append(0)
       
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        user = game_action_container.whose_action
        opponent_color = game_utilities.get_other_player_color(user)
        location_of_other_leader = game_utilities.get_tile_index_of_leader(game_state, opponent_color)
        
        available_tiles = [i for i in game_constants.all_tile_indices 
                           if game_utilities.get_distance_between_tile_indexes(location_of_other_leader, i) <= 2]
        
        available_actions["select_a_tile"] = available_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_per_player[user] < self.influence_tiers[0]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False
        
        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False      

        index_of_tile_to_move_leader_to = game_action_container.required_data_for_action['tile_to_move_leader_to']
        tile_to_move_leader_to = game_state['tiles'][index_of_tile_to_move_leader_to]
        
        if index_of_tile_to_move_leader_to is None or index_of_tile_to_move_leader_to > 8:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False    

        opponent_color = game_utilities.get_other_player_color(user)
        location_of_other_leader = game_utilities.get_tile_index_of_leader(game_state, opponent_color)
        
        if game_utilities.get_distance_between_tile_indexes(location_of_other_leader, index_of_tile_to_move_leader_to) > 2:
            await send_clients_log_message(f"Selected tile is not within 2 tiles of the opponent's leader for **{self.name}**")
            return False

        await send_clients_log_message(f"{user} sent {opponent_color}_leader to **{tile_to_move_leader_to.name}** with **{self.name}**")
        game_state['tiles'][location_of_other_leader].leaders_here[opponent_color] = False
        tile_to_move_leader_to.leaders_here[opponent_color] = True
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True