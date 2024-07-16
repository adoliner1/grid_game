from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Duke(Tile):
    def __init__(self):
        super().__init__(
            name="Duke",
            description = f"Ruling Criteria: Most of any single shape\nRuling Benefits: At the end of the game, +10 points",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        red_shape_counts = {
            'circle': 0,
            'square': 0,
            'triangle': 0
        }
        blue_shape_counts = {
            'circle': 0,
            'square': 0,
            'triangle': 0
        }

        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                if color == "red":
                    red_shape_counts[shape] += 1
                elif color == "blue":
                    blue_shape_counts[shape] += 1

        max_red_shapes = max(red_shape_counts.values())
        max_blue_shapes = max(blue_shape_counts.values())

        if max_red_shapes > max_blue_shapes:
            self.ruler = 'red'
            return 'red'
        elif max_blue_shapes > max_red_shapes:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await callback(f"{self.name} gives 10 points to {ruler}")
            game_state["points"][ruler] += 10
