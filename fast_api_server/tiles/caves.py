import game_utilities
import game_constants
from tiles.tile import Tile

class Caves(Tile):
    def __init__(self):
        super().__init__(
            name="Caves",
            type="Giver/Scorer",
            description="Ruler: Most shapes, minimum 3. When you place a square or a triangle, receive a circle at that tile. If the tile is adjacent to Caves, +4 points as well",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
       
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

    async def on_place_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        shape = data.get('shape')
        index_of_tile_placed_at = data.get('index_of_tile_placed_at')
       
        if shape not in ["square", "triangle"]:
            return
       
        ruler = self.determine_ruler(game_state)
        if ruler != placer:
            return

        index_of_caves = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        is_adjacent = game_utilities.determine_if_directly_adjacent(index_of_caves, index_of_tile_placed_at)
        tile_placed_at = game_state["tiles"][index_of_tile_placed_at]
       
        await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, placer, tile_placed_at, "circle")
        
        if is_adjacent:
            game_state["points"][placer] += 4
            await send_clients_log_message(f"{placer} receives a circle at {tile_placed_at.name} and gains 4 points from {self.name} due to placing a {shape} on an adjacent tile")
        else:
            await send_clients_log_message(f"{placer} receives a circle at {tile_placed_at.name} from {self.name} due to placing a {shape}")