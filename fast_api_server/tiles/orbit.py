import game_utilities
import game_constants
from tiles.tile import Tile

class Orbit(Tile):
    def __init__(self):
        super().__init__(
            name="Orbit",
            description=f"If a player has supremacy in at least two different shapes, they can use Orbit to select a tile. Rotate the row that tile is in left by one\nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game, +5 points.",
            number_of_slots=9,
            data_needed_for_use=["tile_to_shift_row"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        supremacy_count = 0

        shapes = ["circle", "square", "triangle"]
        for shape in shapes:
            player_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == whose_turn_is_it and slot["shape"] == shape)
            opponent_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] != whose_turn_is_it and slot["shape"] == shape)
            if player_count > opponent_count:
                supremacy_count += 1

        return supremacy_count >= 2

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill_in_current_action == "tile_to_shift_row":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")

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

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5
