import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class JestersParty(Tile):
    def __init__(self):
        super().__init__(
            name="Jester's Party",
            type="Generator",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "**Action:** Pay one points for 2 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,  
                    "leader_must_be_present": True,                  
                    "data_needed_for_use": []
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        current_player = game_state["whose_turn_is_it"]

        if (
            not self.influence_tiers[0]["is_on_cooldown"] and
            self.influence_per_player[current_player] >= self.influence_tiers[0]["influence_to_reach_tier"] and
            self.leaders_here[current_player] and
            game_state['leader_movement'][current_player] > 0):
            useable_tiers.append(0)

        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown and cannot be used this round")
            return False
        
        if not self.leaders_here[user]:
            await send_clients_log_message(f"Leader must be on **{self.name}** to use it")
            return False

        await send_clients_log_message(f"**{self.name}** is used")
        game_state['points'][user] -= 1
        game_state['power'][user] += 2
        await send_clients_log_message(f"{user} pays 1 points and gains 2 power from **{self.name}**")
        
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True