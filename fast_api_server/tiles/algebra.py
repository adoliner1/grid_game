from fast_api_server.game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from fast_api_server.tiles.tile import Tile

class Algebra(Tile):
    def __init__(self):
        super().__init__(
            name="Algebra",
            description = f"Ruling Criteria: Most shapes\nRuling Benefits: At the start of the round, produce 1 circle",
            number_of_slots=3,
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

    async def start_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'circle', self.name, callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'circle', self.name, callback)