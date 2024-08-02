import game_utilities
import game_constants
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

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if not ruler:
            await send_clients_log_message(f"No ruler determined for {self.name}, no points awarded")
            return

        adjacent_tiles_indices = game_utilities.get_adjacent_tile_indices(game_utilities.find_index_of_tile_by_name(game_state, self.name))
        adjacent_tiles_ruled_count = 0

        for index in adjacent_tiles_indices:
            tile = game_state["tiles"][index]
            if tile.determine_ruler(game_state) == ruler:
                adjacent_tiles_ruled_count += 1

        points = {0: 0, 1: 1, 2: 3, 3: 7, 4: 13}
        points_awarded = points.get(adjacent_tiles_ruled_count, 0)
        game_state["points"][ruler] += points_awarded
        await send_clients_log_message(f"{ruler} gains {points_awarded} points for ruling tiles adjacent to {self.name}")