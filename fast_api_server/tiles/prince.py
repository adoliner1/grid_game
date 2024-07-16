from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Prince(Tile):
    def __init__(self):
        super().__init__(
            name="Prince",
            description = f"At end of round: Per pair of shapes you have here (e.g. 2 circles), +2 points\nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game +5 points",
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
            pairs = sum(count // 2 for count in shape_count[color].values())
            points_earned = pairs * 2
            game_state["points"][color] += points_earned

            if points_earned > 0:
                await callback(f"{color} player earned {points_earned} points from pairs of shapes on {self.name}")

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await callback(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5
