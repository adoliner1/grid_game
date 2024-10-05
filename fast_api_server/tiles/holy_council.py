from .tile import Tile
from .. import game_utilities
from .. import game_constants

class HolyCouncil(Tile):
    def __init__(self):
        super().__init__(
            name="Holy Council",
            type="Generator",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** If your peak influence is\n**>= 7**, +2 power\n**>= 11**, +3 power\n**>= 15**, +6 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": []
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        peak_influence = game_state["peak_influence"][whose_turn_is_it]
        
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            not self.influence_tiers[0]["is_on_cooldown"] and peak_influence >= 6 and 
            self.determine_ruler(game_state) == whose_turn_is_it):
                useable_tiers.append(0)
        
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        peak_influence = game_state["peak_influence"][user]

        if self.influence_per_player[user] < self.influence_tiers[0]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if not self.determine_ruler(game_state):
            await send_clients_log_message(f"Must rule **{self.name}** ")
            return False

        power_to_give = 0
        if peak_influence >= 15:
            power_to_give = 6
        elif peak_influence >= 11:
            power_to_give = 3
        elif peak_influence >= 7:
            power_to_give = 2
        else:
            await send_clients_log_message(f"{user}'s peak influence is not high enough to gain any power with **{self.name}**")
            return True

        await send_clients_log_message(f"**{self.name}** gives {user} {power_to_give} power")
        game_state['power'][user] += power_to_give
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True