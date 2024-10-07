import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SummoningTree(Tile):
    def __init__(self):
        super().__init__(
            name="Summoning Tree",
            type="Giver",
            number_of_slots=4,
            minimum_influence_to_rule=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "**Action:** [[Receive]] a sage at Summoning Tree",
                    "is_on_cooldown": False,
                    "leader_must_be_present": True,
                    "data_needed_for_use": [],
                    "has_a_cooldown": True,
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        current_player = game_state["whose_turn_is_it"]
        if (not self.influence_tiers[0]["is_on_cooldown"] and 
            self.influence_per_player[current_player] >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            self.leaders_here[current_player]):
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action                                              

        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown and cannot be used this round")
            return False
       
        if not self.leaders_here[user]:
            await send_clients_log_message(f"Leader must be on **{self.name}** to use it")
            return False
       
        await send_clients_log_message(f"**{self.name}** is used")
        await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, user, self, 'sage')
        
        self.influence_tiers[0]['is_on_cooldown'] = True
        return True