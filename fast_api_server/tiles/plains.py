import game_utilities
import game_constants
from tiles.tile import Tile

class Plains(Tile):
    def __init__(self):
        super().__init__(
            name="Plains",
            description=f"Ruling Criteria: 4 or more shapes\nRuling Benefits: When an adjacent tile produces shapes, Plains produces one more of the same type",
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
        if red_count >= 3 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 3 and blue_count > red_count:
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
        adjacent_indices = self.get_adjacent_tiles_indices(game_state)

        if producing_tile_index in adjacent_indices:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, 1, shape, self.name)

    def get_adjacent_tiles_indices(self, game_state):
        tile_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        return game_utilities.get_adjacent_tile_indices(tile_index)