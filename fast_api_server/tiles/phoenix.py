import game_utilities
import game_constants
from tiles.tile import Tile

class Phoenix(Tile):
    def __init__(self):
        super().__init__(
            name="Phoenix",
            type="Producer",
            description="Ruler: Most shapes, minimum 2. After a shape is burned at a tile, if you have 3 power there, produce a circle and +1 point",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        
        if red_count > blue_count and red_count >= 2:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count and blue_count >= 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')
        
        ruler = self.determine_ruler(game_state)
        if not ruler:
            return
        
        tile_burned_at = game_state["tiles"][index_of_tile_burned_at]
        ruler_power_at_tile = tile_burned_at.power_per_player[ruler]
        
        if ruler_power_at_tile < 3:
            return
        
        await send_clients_log_message(f"{self.name} triggers for {ruler}")
        await game_utilities.produce_shape_for_player(
            game_state,
            game_action_container_stack,
            send_clients_log_message,
            send_clients_available_actions,
            send_clients_game_state,
            ruler,
            1,
            "circle",
            self.name
        )
        
        game_state["points"][ruler] += 1
        await send_clients_log_message(f"{ruler} gains 1 point from {self.name}")