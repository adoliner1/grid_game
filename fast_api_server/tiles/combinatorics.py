from game_utilities import produce_shape_for_player
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            description = f"Ruling Criteria: Most pairs\nRuling Benefits: At the end of the round, per pair here, produce 1 shape of that type",
            number_of_slots=8,
        )

    def determine_ruler(self, game_state):
        red_pairs = {"circle": 0, "square": 0, "triangle": 0}
        blue_pairs = {"circle": 0, "square": 0, "triangle": 0}

        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                if color == "red":
                    red_pairs[shape] += 1
                elif color == "blue":
                    blue_pairs[shape] += 1

        red_pair_count = sum(count // 2 for count in red_pairs.values())
        blue_pair_count = sum(count // 2 for count in blue_pairs.values())

        if red_pair_count > blue_pair_count:
            self.ruler = 'red'
            return 'red'
        elif blue_pair_count > red_pair_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler is None:
            return

        pair_counts = {"circle": 0, "square": 0, "triangle": 0}
        for slot in self.slots_for_shapes:
            if slot and slot["color"] == ruler:
                shape = slot["shape"]
                pair_counts[shape] += 1

        for shape, count in pair_counts.items():
            pairs = count // 2
            if pairs > 0:
                await produce_shape_for_player(game_state, ruler, pairs, shape, self.name, callback)