import game_utilities
import game_constants
from tiles.tile import Tile

class Sword(Tile):
    def __init__(self):
        super().__init__(
            name="Sword",
            description = f"Ruling Criteria: 3 or more shapes\nRuling Benefits: You may use this tile to burn one of your shapes here and a shape on an adjacent tile",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_burn_shape_from", "slot_and_tile_to_burn_shape_at"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it
    
    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_burn_shape_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, self.determine_ruler(game_state), game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        else:
            slots_with_a_burnable_shape = {}
            indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["index_of_tile_in_use"])
            for index in indices_of_adjacent_tiles:
                slots_with_shapes = []
                for slot_index, slot in enumerate(game_state["tiles"][index].slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_burnable_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        self.determine_ruler(game_state)
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False

        index_of_sword = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_shape_from_here = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_from']['slot_index']
        slot_index_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['slot_index']
        index_of_tile_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_sword, index_of_tile_to_burn_shape_at):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False
        
        if self.slots_for_shapes[slot_index_to_burn_shape_from_here] == None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to burn at {self.name}")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_shape_at].slots_for_shapes[slot_index_to_burn_shape_at] == None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape_at].name}")
            return False

        if self.slots_for_shapes[slot_index_to_burn_shape_from_here]["color"] != self.ruler:
            await send_clients_log_message(f"Tried to use {self.name} but chose shape that didn't belong to them")
            return False
        
        await send_clients_log_message(f"Using {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_sword, slot_index_to_burn_shape_from_here)
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_burn_shape_at, slot_index_to_burn_shape_at)

        return True