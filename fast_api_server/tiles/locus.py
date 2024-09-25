import game_utilities
import game_constants
from tiles.tile import Tile

class Locus(Tile):
    def __init__(self):
        super().__init__(
            name="Locus",
            type="Generator",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** Gain 2 power for each adjacent tile you rule",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": [],
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        user = game_state["whose_turn_is_it"]
        if (not self.influence_tiers[0]['is_on_cooldown'] and 
            self.influence_per_player[user] >= self.influence_tiers[0]['influence_to_reach_tier'] and user == self.determine_ruler(game_state)):
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
       
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** tier {tier_index} is on cooldown")
            return False
       
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use tier {tier_index}")
            return False
       
        if self.determine_ruler(game_state) != user:
            await send_clients_log_message(f"You must be the ruler to use **{self.name}**")
            return False

        index_of_locus = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        adjacent_tiles_ruled = 0
        power_gained = 0
        for tile_index in game_utilities.get_adjacent_tile_indices(index_of_locus):
            if game_state['tiles'][tile_index].determine_ruler(game_state) == user:
                adjacent_tiles_ruled += 1

        power_gained = adjacent_tiles_ruled*2
        game_state['power'][user] += power_gained
        await send_clients_log_message(f"{user} uses **{self.name}** and gains {power_gained} power") 
       
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True