import game_utilities
import game_constants
from tiles.tile import Tile

class Ash(Tile):
    def __init__(self):
        super().__init__(
            name="Ash",
            description=f"Ruling Criteria: Most shapes, minimum 2\nRuling Benefits: When a shape is burned on an adjacent tile, +2 points.",
            number_of_slots=3,
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
        index_of_ash = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if not game_utilities.determine_if_directly_adjacent(index_of_ash, index_of_tile_burned_at):
            return
        
        ruler = self.determine_ruler(game_state)
        if not ruler:
            return
        
        game_state["points"][ruler] += 2
        await send_clients_log_message(f"{ruler} gains 2 points from {self.name} due to a shape being burned on an adjacent tile")