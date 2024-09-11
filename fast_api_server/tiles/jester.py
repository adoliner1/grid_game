import game_utilities
import game_constants
from tiles.tile import Tile

class Jester(Tile):
    def __init__(self):
        super().__init__(
            name="Jester",
            type="Scorer",
            minimum_power_to_rule=1,
            description = f"At the __end of a round__, per unique type of pair you have here, +5 points",
            number_of_slots=9,
            power_tiers=[
                {
                    "power_to_reach_tier": 1,
                    "must_be_ruler": True,                    
                    "description": "At the __end of the game__, -10 points",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                     
                },
            ]            

        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        for color in ['red', 'blue']:
            shapes = [slot["shape"] for slot in self.slots_for_shapes if slot and slot["color"] == color]
            max_pairs = game_utilities.find_max_unique_pairs(shapes, set())
            points_earned = max_pairs * 5
            game_state["points"][color] += points_earned
            if points_earned > 0:
                await send_clients_log_message(f"{color} player earned {points_earned} points from unique pairs on {self.name}")

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await send_clients_log_message(f"{ruler} rules {self.name}, -10 points")
            game_state["points"][ruler] -= 10