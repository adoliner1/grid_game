import game_utilities
import game_constants
from tiles.tile import Tile

class Pluto(Tile):
    def __init__(self):
        super().__init__(
            name="Pluto",
            type="Producer",
            minimum_power_to_rule=2,
            number_of_slots=7,
            power_tiers=[
                {
                    "power_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ 2 circles here to ++produce++ a square",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": []
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": True,                    
                    "description": "**Action:** ^^Burn^^ 1 circle here to ++produce++ a square",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": [],
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        
        player_power = self.power_per_player[whose_turn_is_it]
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it)

        if not self.power_tiers[0]['is_on_cooldown'] and player_power >= 2 and circle_count >= 2:
            useable_tiers.append(0)
        if not self.power_tiers[1]['is_on_cooldown'] and player_power >= 5 and circle_count >= 1 and whose_turn_is_it == ruler:
            useable_tiers.append(1)

        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if self.power_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"Tier {tier_index} at {self.name} is on cooldown")
            return False

        player_power = self.power_per_player[player]
        required_power = self.power_tiers[tier_index]['power_to_reach_tier']

        if player_power < required_power:
            await send_clients_log_message(f"{player} does not have enough power to use tier {tier_index} of {self.name}")
            return False

        if tier_index == 1 and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier 1 of {self.name}")
            return False

        circles_to_burn = [
            i for i, slot in enumerate(self.slots_for_shapes)
            if slot and slot["shape"] == "circle" and slot["color"] == player
        ]

        circles_required = 2 if tier_index == 0 else 1
        if len(circles_to_burn) < circles_required:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False

        await send_clients_log_message(f"{self.name} tier {tier_index} is used")
        for i in circles_to_burn[:circles_required]:
            await game_utilities.burn_shape_at_tile_at_index(
                game_state, game_action_container_stack, send_clients_log_message, 
                get_and_send_available_actions, send_clients_game_state, 
                game_utilities.find_index_of_tile_by_name(game_state, self.name), i
            )

        await game_utilities.produce_shape_for_player(
            game_state, game_action_container_stack, send_clients_log_message, 
            get_and_send_available_actions, send_clients_game_state, 
            player, 1, 'square', self.name, True
        )

        self.power_tiers[tier_index]['is_on_cooldown'] = True
        return True