import game_utilities
import game_constants
from tiles.tile import Tile

class Jester(Tile):
    def __init__(self):
        super().__init__(
            name="Jester",
            description = f"At the end of the round, per unique type of pair you have here gain 5 points\nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game, -10 points",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        for color in ['red', 'blue']:
            shapes = [slot["shape"] for slot in self.slots_for_shapes if slot and slot["color"] == color]
            max_pairs = game_utilities.find_max_unique_pairs(shapes, set())
            points_earned = max_pairs * 5
            game_state["points"][color] += points_earned
            if points_earned > 0:
                await send_clients_log_message(f"{color} player earned {points_earned} points from unique pairs on {self.name}")

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await send_clients_log_message(f"{self.name} makes {ruler} lose 10 points")
            game_state["points"][ruler] -= 10