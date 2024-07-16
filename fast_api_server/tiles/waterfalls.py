from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile, find_index_of_tile_by_name, determine_if_directly_adjacent
from tiles.tile import Tile

class Waterfalls(Tile):
    def __init__(self):
        super().__init__(
            name="Waterfall",
            description=f"\nRuling Criteria: most shapes, minimum 3\nRuling Benefits: At the end of the round, gain points based on the number of adjacent tiles you also rule. 0 or 1: 1, 2: 3, 3: 7, 4: 13",
            number_of_slots=5,
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
        if red_count >= 3 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 3 and blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if not ruler:
            await callback(f"No ruler determined for {self.name}, no points awarded")
            return

        adjacent_tiles_indices = self.get_adjacent_tiles_indices(game_state)
        adjacent_tiles_ruled_count = 0

        for index in adjacent_tiles_indices:
            tile = game_state["tiles"][index]
            if tile.determine_ruler(game_state) == ruler:
                adjacent_tiles_ruled_count += 1

        points = {0: 0, 1: 1, 2: 3, 3: 7, 4: 13}
        points_awarded = points.get(adjacent_tiles_ruled_count, 0)
        game_state["points"][ruler] += points_awarded
        await callback(f"{ruler} gains {points_awarded} points for ruling tiles adjacent to {self.name}")

    def get_adjacent_tiles_indices(self, game_state):
        tile_index = find_index_of_tile_by_name(game_state, self.name)
        adjacent_indices = []

        if tile_index % 3 != 0:  # Not in the first column
            adjacent_indices.append(tile_index - 1)
        if tile_index % 3 != 2:  # Not in the last column
            adjacent_indices.append(tile_index + 1)
        if tile_index // 3 != 0:  # Not in the first row
            adjacent_indices.append(tile_index - 3)
        if tile_index // 3 != 2:  # Not in the last row
            adjacent_indices.append(tile_index + 3)

        return adjacent_indices