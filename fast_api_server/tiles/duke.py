import game_utilities
import game_constants
from tiles.tile import Tile

class Duke(Tile):
    def __init__(self):
        super().__init__(
            name="Duke",
            type="Scorer",
            description="**Ruler, Most of any Shape Type, Minimum 2 of that Shape:** At the end of the game, +7 points",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        shape_counts = {
            'red': {'circle': 0, 'square': 0, 'triangle': 0},
            'blue': {'circle': 0, 'square': 0, 'triangle': 0}
        }

        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                shape_counts[color][shape] += 1

        max_shapes = {
            'red': max(shape_counts['red'].values()),
            'blue': max(shape_counts['blue'].values())
        }

        if max_shapes['red'] > max_shapes['blue'] and max_shapes['red'] >= 2:
            self.ruler = 'red'
            return 'red'
        elif max_shapes['blue'] > max_shapes['red'] and max_shapes['blue'] >= 2:
            self.ruler = 'blue'
            return 'blue'
        
        self.ruler = None
        return None

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 7 points to {ruler}")
            game_state["points"][ruler] += 7