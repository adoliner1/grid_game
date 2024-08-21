import game_utilities
import game_constants
from tiles.tile import Tile

class RedDwarf(Tile):
    def __init__(self):
        super().__init__(
            name="Red Dwarf",
            type="Tile-Mover/Scorer",
            description=f"Action: Burn one of your shapes here to swap the position of a tile with an adjacent tile\nRuler: Most Shapes",
            number_of_slots=3,
            data_needed_for_use=["slot_to_burn_from_on_red_dwarf", "first_tile", "adjacent_tile_to_first_tile"]
        )

    def is_useable(self, game_state):
        return any(slot for slot in self.slots_for_shapes if slot and slot["color"] == game_state["whose_turn_is_it"])

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill == "slot_to_burn_from_on_red_dwarf":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill == "first_tile":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill == "adjacent_tile_to_first_tile":
            first_tile_index = game_action_container.required_data_for_action["first_tile"]
            if first_tile_index is not None:
                available_actions["select_a_tile"] = game_utilities.get_adjacent_tile_indices(first_tile_index)

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
        
        if not self.is_useable(game_state):
            await send_clients_log_message(f"{self.name} is on cooldown or player has no shapes to burn")
            return False

        slot_to_burn_from_on_red_dwarf = game_action_container.required_data_for_action['slot_to_burn_from_on_red_dwarf']['slot_index']
        tile1_index = game_action_container.required_data_for_action['first_tile']
        tile2_index = game_action_container.required_data_for_action['adjacent_tile_to_first_tile']

        if slot_to_burn_from_on_red_dwarf is None or tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid shape or tiles selected for using {self.name}")
            return False

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for {self.name}")
            return False

        if tile2_index not in game_utilities.get_adjacent_tile_indices(tile1_index):
            await send_clients_log_message(f"Selected tiles are not adjacent for {self.name}")
            return False

        if self.slots_for_shapes[slot_to_burn_from_on_red_dwarf]["color"] != game_action_container.whose_action:
            await send_clients_log_message(f"Cannot burn other player's shape")
            return False
        
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), slot_to_burn_from_on_red_dwarf)
        await send_clients_log_message(f"Using {self.name} to swap tiles at indices {tile1_index} and {tile2_index}")
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        return True