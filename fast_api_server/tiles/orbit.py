import game_utilities
import game_constants
from tiles.tile import Tile

class Orbit(Tile):
    def __init__(self):
        super().__init__(
            name="Orbit",
            type="Tile-Mover",
            description=f"Ruler: Most shapes, Action: Once per round, choose a tile. Rotate the row that tile is in left once",
            number_of_slots=5,
            data_needed_for_use=["tile_to_shift_row"]
        )

    def is_useable(self, game_state):
        return self.determine_ruler(game_state) == game_state["whose_turn_is_it"] and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill_in_current_action == "tile_to_shift_row":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False

        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False

        tile_to_shift_row = game_action_container.required_data_for_action['tile_to_shift_row']

        if tile_to_shift_row is None:
            await send_clients_log_message(f"Invalid tile selected for using {self.name}")
            return False

        # Determine the row from the tile index
        row_to_shift = tile_to_shift_row // 3

        await send_clients_log_message(f"Using {self.name} to shift row {row_to_shift}")

        # Shift the row of tiles
        row_start_index = row_to_shift * 3
        row_end_index = row_start_index + 3
        row_tiles = game_state["tiles"][row_start_index:row_end_index]

        # Perform the shift
        shifted_row_tiles = row_tiles[1:] + row_tiles[:1]

        # Update the game state with the shifted row
        game_state["tiles"][row_start_index:row_end_index] = shifted_row_tiles
        self.is_on_cooldown = True

        return True
