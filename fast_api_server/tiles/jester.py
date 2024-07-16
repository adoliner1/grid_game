from game_utilities import produce_shape_for_player
from tiles.tile import Tile

class Jester(Tile):
    def __init__(self):
        super().__init__(
            name="Jester",
            description = f"At the end of the round, per triple you have here (one circle, square, and triangle) gain 7 points\nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game, the ruler loses 10 points",
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

    async def end_of_round_effect(self, game_state, callback):
        shape_count = {
            'red': {
                'circle': 0,
                'square': 0,
                'triangle': 0
            },
            'blue': {
                'circle': 0,
                'square': 0,
                'triangle': 0
            }
        }

        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                shape_count[color][shape] += 1

        for color in ['red', 'blue']:
            triples = min(shape_count[color]['circle'], shape_count[color]['square'], shape_count[color]['triangle'])
            points_earned = triples * 7
            game_state["points"][color] += points_earned

            if points_earned > 0:
                await callback(f"{color} player earned {points_earned} points from triples on {self.name}")

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await callback(f"{self.name} makes {ruler} lose 10 points")
            game_state["points"][ruler] -= 10
