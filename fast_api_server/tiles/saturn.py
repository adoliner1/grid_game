import game_utilities
import game_constants
from tiles.tile import Tile

class Saturn(Tile):
    def __init__(self):
        super().__init__(
            name="Saturn",
            type="Producer",
            minimum_power_to_rule=3,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "**Action:** ^^Burn^^ one of your triangles here to ++produce++ a square and a circle",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                     
                    "data_needed_for_use": [] 
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": False,
                    "description": "**Action:** Same as above but ++produce++ 2 squares",
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
        player_power = self.power_per_player[whose_turn_is_it]

        has_triangle = any(slot and slot["shape"] == "triangle" and slot["color"] == whose_turn_is_it
                           for slot in self.slots_for_shapes)

        if has_triangle:
            if not self.power_tiers[0]["is_on_cooldown"] and player_power >= 3:
                useable_tiers.append(0)
            if not self.power_tiers[1]["is_on_cooldown"] and player_power >= 5:
                useable_tiers.append(1)

        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        player_power = self.power_per_player[player]

        if player_power < self.power_tiers[tier_index]["power_to_reach_tier"]:
            await send_clients_log_message(f"Not enough power to use tier {tier_index} of {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False

        triangle_slot = next((i for i, slot in enumerate(self.slots_for_shapes) 
                              if slot and slot["shape"] == "triangle" and slot["color"] == player), None)

        if triangle_slot is None:
            await send_clients_log_message(f"No triangle to burn on {self.name}")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of {self.name}")
        saturn_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, 
                                                         send_clients_log_message, get_and_send_available_actions, 
                                                         send_clients_game_state, saturn_index, triangle_slot)

        if tier_index == 0:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, 
                                                          send_clients_log_message, get_and_send_available_actions, 
                                                          send_clients_game_state, player, 1, 'square', self.name, True)
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, 
                                                          send_clients_log_message, get_and_send_available_actions, 
                                                          send_clients_game_state, player, 1, 'circle', self.name, True)
        else:
            for _ in range(2):
                await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, 
                                                              send_clients_log_message, get_and_send_available_actions, 
                                                              send_clients_game_state, player, 1, 'square', self.name, True)

        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True