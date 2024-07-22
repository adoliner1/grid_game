from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile, find_index_of_tile_by_name, determine_if_directly_adjacent
from tiles.tile import Tile

class Caves(Tile):
    def __init__(self):
        super().__init__(
            name="Caves",
            description = f"Ruling Criteria: 3 or more shapes\nRuling Benefits: When you place a square or a triangle on an adjacent tile, produce a circle.",
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
        if red_count > blue_count and red_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count and blue_count >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_place"][self.name] = self.on_place_effect

    async def on_place_effect(self, game_state, callback, **data):
            placer = data.get('placer')
            shape = data.get('shape')

            if shape == "circle":
                return
            
            index_of_tile_placed_at = data.get('index_of_tile_placed_at')
            index_of_caves = find_index_of_tile_by_name(game_state, self.name)

            if not determine_if_directly_adjacent(index_of_caves, index_of_tile_placed_at):
                return

            ruler = self.determine_ruler(game_state)
            if ruler != placer:
                return

            await produce_shape_for_player(game_state, placer, 1, "circle", self.name, callback)