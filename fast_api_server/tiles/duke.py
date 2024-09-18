import game_utilities
import game_constants
from tiles.tile import Tile

class Duke(Tile):
    def __init__(self):
        super().__init__(
            name="Duke",
            type="Scorer",
            minimum_influence_to_rule=3,
            influence_tiers=[],
            description="For each shape type you have more of here at the end of the game, +3 points. If it's all of them, +5 points more",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        shape_counts = {
            'red': {'circle': 0, 'square': 0, 'triangle': 0},
            'blue': {'circle': 0, 'square': 0, 'triangle': 0}
        }
        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                shape_counts[color][shape] += 1

        points = {'red': 0, 'blue': 0}
        shapes_dominated = {'red': 0, 'blue': 0}

        for shape in game_constants.shapes:
            if shape_counts['red'][shape] > shape_counts['blue'][shape]:
                points['red'] += 3
                shapes_dominated['red'] += 1
                await send_clients_log_message(f"Red has more {shape}s on {self.name}, +3 points")
            elif shape_counts['blue'][shape] > shape_counts['red'][shape]:
                points['blue'] += 3
                shapes_dominated['blue'] += 1
                await send_clients_log_message(f"Blue has more {shape}s on {self.name}, +3 points")

        for color in ['red', 'blue']:
            if shapes_dominated[color] == len(game_constants.shapes):
                points[color] += 5
                await send_clients_log_message(f"{color} has more of all shape types on {self.name}, +5 points")