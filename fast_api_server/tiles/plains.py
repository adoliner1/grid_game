import game_utilities
import game_constants
from tiles.tile import Tile

class Plains(Tile):
    def __init__(self):
        super().__init__(
            name="Plains",
            type="Producer/Scorer",
            description="Ruler: More of at least 2 shape types. When a tile you're present at produces shapes, +1 point. If it's adjacent to Plains also, produce one of that shape instead",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        shape_counts = {
            'red': {'circle': 0, 'square': 0, 'triangle': 0},
            'blue': {'circle': 0, 'square': 0, 'triangle': 0}
        }
        for slot in self.slots_for_shapes:
            if slot:
                color = slot["color"]
                shape = slot["shape"]
                if color in shape_counts and shape in shape_counts[color]:
                    shape_counts[color][shape] += 1
        supremacy_count = {'red': 0, 'blue': 0}
        for shape in ['circle', 'square', 'triangle']:
            if shape_counts['red'][shape] > shape_counts['blue'][shape]:
                supremacy_count['red'] += 1
            elif shape_counts['blue'][shape] > shape_counts['red'][shape]:
                supremacy_count['blue'] += 1
        if supremacy_count['red'] >= 2:
            self.ruler = 'red'
            return 'red'
        elif supremacy_count['blue'] >= 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_produce"][self.name] = self.on_produce_effect

    async def on_produce_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        producing_tile_name = data.get('producing_tile_name')
        shape = data.get('shape')
        ruler = self.determine_ruler(game_state)
        if not ruler:
            return

        producing_tile_index = game_utilities.find_index_of_tile_by_name(game_state, producing_tile_name)
        producing_tile = game_state["tiles"][producing_tile_index]

        # Check if ruler is present at the producing tile
        if not game_utilities.has_presence(producing_tile, ruler):
            return

        plains_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        is_adjacent = game_utilities.determine_if_directly_adjacent(plains_index, producing_tile_index)

        if is_adjacent:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, 1, shape, self.name)
            await send_clients_log_message(f"{ruler} produces 1 {shape} from {self.name} due to adjacent production")
        else:
            game_state["points"][ruler] += 1
            await send_clients_log_message(f"{ruler} gains 1 point from {self.name} due to production")