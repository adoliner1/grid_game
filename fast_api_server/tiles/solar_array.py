import game_utilities
import game_constants
from tiles.tile import Tile

class SolarArray(Tile):
    def __init__(self):
        super().__init__(
            name="Solar Array",
            type="Scorer",
            minimum_power_to_rule=2,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ all your shapes here. If you burned 2 or more and your peak power is:\n **>= 6:** +3 points\n**>= 10:** +7 points\n**>= 14:** +12 points",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                 
                    "data_needed_for_use": []
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        if ruler == whose_turn_is_it and self.power_per_player[whose_turn_is_it] >= 3 and not self.power_tiers[0]["is_on_cooldown"]:
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"{game_action_container.whose_action} is not the ruler of {self.name} and cannot use it")
            return False
        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False
        solar_array_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        shapes_burned = 0
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == ruler:
                await game_utilities.burn_shape_at_tile_at_index(
                    game_state, game_action_container_stack, send_clients_log_message,
                    get_and_send_available_actions, send_clients_game_state,
                    solar_array_index, i
                )
                shapes_burned += 1
        await send_clients_log_message(f"{ruler} burned {shapes_burned} shapes on {self.name}")
        peak_power = game_state["peak_power"][ruler]
        points_gained = 0
        if shapes_burned >= 2:
            if peak_power >= 14:
                points_gained = 12
            elif peak_power >= 10:
                points_gained = 7
            elif peak_power >= 6:
                points_gained = 3
        if points_gained > 0:
            game_state["points"][ruler] += points_gained
            await send_clients_log_message(f"{ruler} gains {points_gained} points from {self.name}")
        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True