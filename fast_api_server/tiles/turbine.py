import game_utilities
import game_constants
from tiles.tile import Tile

class Turbine(Tile):
    def __init__(self):
        super().__init__(
            name="Turbine",
            type="Producer",
            minimum_power_to_rule=2,
            number_of_slots=3,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "**Action:** If your peak power is\n**>= 6**, +1 stamina\n**>= 10**, +2 stamina\n**>= 14**, +3 stamina",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": []
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        peak_power = game_state["peak_power"][whose_turn_is_it]
        
        if (self.power_per_player[whose_turn_is_it] >= self.power_tiers[0]["power_to_reach_tier"] and 
            not self.power_tiers[0]["is_on_cooldown"] and peak_power >= 6):
            useable_tiers.append(0)
        
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        peak_power = game_state["peak_power"][user]

        if self.power_per_player[user] < self.power_tiers[0]["power_to_reach_tier"]:
            await send_clients_log_message(f"Not enough power to use {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"{self.name} is on cooldown")
            return False

        stamina_to_give = 0
        if peak_power >= 14:
            stamina_to_give = 3
        elif peak_power >= 10:
            stamina_to_give = 2
        elif peak_power >= 6:
            stamina_to_give = 1
        else:
            await send_clients_log_message(f"{user}'s peak power is not high enough to gain any stamina with {self.name}")
            return True

        await send_clients_log_message(f"{self.name} gives {user} {stamina_to_give} stamina")
        game_state['stamina'][user] += stamina_to_give
        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True