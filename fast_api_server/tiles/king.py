from game_utilities import produce_shape_for_player, find_index_of_tile_by_name, determine_if_directly_adjacent
from tiles.tile import Tile

class King(Tile):
    def __init__(self):
        super().__init__(
            name="King",
            description = f"Ruling Criteria: Most shapes, minimum 6\nRuling Benefits: At the end of the game +20 points",
            number_of_slots=11,
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
        if red_count >= 6 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 6 and blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await callback(f"{self.name} gives 20 points to {ruler}")
            game_state["points"][ruler] += 20
