import game_utilities
import game_constants
from tiles.tile import Tile

class Queen(Tile):
    def __init__(self):
        super().__init__(
            name="Queen",
            type="Scorer",
            description="**Ruler, Most Shapes, Minimum 3:** Whenever a shape is ((placed)) here by the non-ruler, +2 points. At the end of the game, +7 points",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        red_shape_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_shape_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        
        if red_shape_count > blue_shape_count and red_shape_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_shape_count > red_shape_count and blue_shape_count >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_place"][self.name] = self.on_place_effect

    async def on_place_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        tile_index = data.get('index_of_tile_placed_at')
        if tile_index != game_utilities.find_index_of_tile_by_name(game_state, self.name):
            return
        
        ruler = self.determine_ruler(game_state)
        if ruler and placer != ruler:
            game_state["points"][ruler] += 2
            await send_clients_log_message(f"{ruler} earned 2 points as the ruler of {self.name}")

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            await send_clients_log_message(f"{self.name} gives 7 points to {ruler}")
            game_state["points"][ruler] += 7