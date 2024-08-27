import game_utilities
import game_constants
from tiles.tile import Tile

class RedDwarf(Tile):
    def __init__(self):
        super().__init__(
            name="Red Dwarf",
            type="Tile-Mover",
            description="**Action:** ^^Burn^^ one of your shapes here to swap the position of 2 tiles\n**Ruler: Most Shapes**",
            number_of_slots=3,
            data_needed_for_use=["slot_to_burn_from_on_red_dwarf", "first_tile", "second_tile"]
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
        elif current_piece_of_data_to_fill == "second_tile":
            first_tile = game_action_container.required_data_for_action.get("first_tile")
            available_tiles = list(range(len(game_state["tiles"])))
            if first_tile is not None:
                available_tiles.remove(first_tile)
            available_actions["select_a_tile"] = available_tiles

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
            await send_clients_log_message(f"{self.name} cannot be used - no shapes to burn")
            return False

        slot_to_burn_from = game_action_container.required_data_for_action['slot_to_burn_from_on_red_dwarf']['slot_index']
        tile1_index = game_action_container.required_data_for_action['first_tile']
        tile2_index = game_action_container.required_data_for_action['second_tile']

        if any(index is None for index in [slot_to_burn_from, tile1_index, tile2_index]):
            await send_clients_log_message(f"Invalid shape or tiles selected for using {self.name}")
            return False

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot swap a tile with itself using {self.name}")
            return False

        if self.slots_for_shapes[slot_to_burn_from]["color"] != game_action_container.whose_action:
            await send_clients_log_message(f"Cannot burn another player's shape on {self.name}")
            return False
        
        red_dwarf_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, red_dwarf_index, slot_to_burn_from)
        await send_clients_log_message(f"Used {self.name} to swap {game_state['tiles'][tile1_index].name} and {game_state['tiles'][tile2_index].name}")
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        return True