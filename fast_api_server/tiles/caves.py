import game_utilities
import game_constants
from tiles.tile import Tile

class Caves(Tile):
    def __init__(self):
        super().__init__(
            name="Caves",
            type="Giver/Scorer",
            description="3 Power: When you place a triangle at an adjacent tile, receive a circle at that tile\n6 Power: adjacent or anywhere you're present\n9 Power: receive a square instead\nRuler: Most Power",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"]:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"]:
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
       
        if shape != "triangle":
            return
       
        self.determine_power()
        placer_power = self.power_per_player[placer]
        if placer_power < 3:
            return

        index_of_caves = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        is_adjacent = game_utilities.determine_if_directly_adjacent(index_of_caves, index_of_tile_placed_at)
        tile_placed_at = game_state["tiles"][index_of_tile_placed_at]

        if placer_power < 6 and not is_adjacent:
            return

        if placer_power >= 6 and not (is_adjacent or game_utilities.has_presence(tile_placed_at, placer)):
            return

        shape_to_receive = "square" if placer_power >= 9 else "circle"
       
        await game_utilities.player_receives_a_shape_on_tile(
            game_state, game_action_container_stack, send_clients_log_message, 
            send_clients_available_actions, send_clients_game_state, 
            placer, tile_placed_at, shape_to_receive
        )

        await send_clients_log_message(f"{placer} receives a {shape_to_receive} at {tile_placed_at.name} from {self.name}")