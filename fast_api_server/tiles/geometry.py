from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Geometry(Tile):
    def __init__(self):
        super().__init__(
            name="Geometry",
            description = f"Ruling Criteria: Most shapes, minimum 4\nRuling Benefits: At the start of the round, produce 1 triangle. At the end of the game +2 points",
            number_of_slots=7,
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
        if red_count > blue_count and red_count >= 4:
            self.ruler = 'red'
            return 'red'
        elif blue_count < red_count and blue_count >= 4:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'triangle', self.name, callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'triangle', self.name, callback)

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await callback(f"{self.name} gives 2 points to {ruler}")
            game_state["points"][ruler] += 2
