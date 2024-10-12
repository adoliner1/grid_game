import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class CrystalShrine(Tile):
    def __init__(self):
        super().__init__(
            name="Crystal Shrine",
            type="Generator",
            number_of_slots=4,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 11,
                    "must_be_ruler": True,                    
                    "description": "**Action**: If Crystal Shrine is full, +8 power",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_a_cooldown": True,
                    "data_needed_for_use": [],
                }
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if (ruler == whose_turn_is_it and 
            self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier'] and 
            None not in self.slots_for_disciples and not self.influence_tiers[0]['is_on_cooldown']):
            useable_tiers.append(0)
        
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False

        if self.influence_per_player[user] < self.influence_tiers[0]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False

        if None in self.slots_for_disciples:
            await send_clients_log_message(f"**{self.name}** is not full")
            return False
        
        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        power_to_gain = 8
        game_state['power'][user] += power_to_gain
        await send_clients_log_message(f"**{self.name}** gives {power_to_gain} power to {user}")

        self.influence_tiers[0]['is_on_cooldown'] = True
        return True