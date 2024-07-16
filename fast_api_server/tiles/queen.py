from game_utilities import produce_shape_for_player, find_index_of_tile_by_name, determine_if_directly_adjacent
from tiles.tile import Tile

class Queen(Tile):
    def __init__(self):
        super().__init__(
            name="Queen",
            description = f"When you place a shape on this tile, +1 point\nRuling Criteria: Most squares, minimum 3\nRuling Benefits: At the end of the game, +5 points",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "square":
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

    def setup_listener(self, game_state):
        game_state["listeners"]["on_place"][self.name] = self.on_place_effect

    async def on_place_effect(self, game_state, callback, **data):
        placer = data.get('placer')
        tile_index = data.get('index_of_tile_placed_at')

        if tile_index != find_index_of_tile_by_name(game_state, self.name):
            return

        game_state["points"][placer] += 1
        await callback(f"{placer} earned 1 point for placing a shape on {self.name}")

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await callback(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5
