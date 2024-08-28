import game_utilities
import game_constants
from tiles.tile import Tile

class TeleportingCabinet(Tile):
    def __init__(self):
        super().__init__(
            name="Teleporting Cabinet",
            type="Mover",
            description=f"**Ruler, Most Shapes, Action:** Once per round, choose a shape at an adjacent tile and swap it with a shape anywhere",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_swap_shape_from", "slot_and_tile_to_swap_shape_to"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_swap_shape_from":
            adjacent_slots_with_a_shape = {}
            indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["index_of_tile_in_use"])
            for index in indices_of_adjacent_tiles:
                slots_with_shapes = []
                for slot_index, slot in enumerate(game_state["tiles"][index].slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    adjacent_slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = adjacent_slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_swap_shape_to":
            slots_with_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape

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
        self.determine_ruler(game_state)
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False

        index_of_cabinet = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        game_action_container.required_data_for_action
        slot_index_to_swap_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_from']['slot_index']
        index_of_tile_to_swap_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_from']['tile_index']
        slot_index_to_swap_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_to']['slot_index']
        index_of_tile_to_swap_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_to']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_cabinet, index_of_tile_to_swap_shape_from):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False

        if game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_index_to_swap_shape_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to swap from {game_state['tiles'][index_of_tile_to_swap_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_index_to_swap_shape_to] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to swap to {game_state['tiles'][index_of_tile_to_swap_shape_to].name}")
            return False

        slot_data_to_swap_from = game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_index_to_swap_shape_from]
        slot_data_to_swap_to = game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_index_to_swap_shape_to]

        await send_clients_log_message(f"Using {self.name}")

        # Swap shapes
        game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_index_to_swap_shape_from] = slot_data_to_swap_to
        game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_index_to_swap_shape_to] = slot_data_to_swap_from

        game_utilities.determine_power_levels(game_state)
        game_utilities.update_presence(game_state)
        game_utilities.determine_rulers(game_state)
        await send_clients_log_message(f"Swapped {slot_data_to_swap_from['shape']} from {game_state['tiles'][index_of_tile_to_swap_shape_from].name} with {slot_data_to_swap_to['shape']} at {game_state['tiles'][index_of_tile_to_swap_shape_to].name}")
        self.is_on_cooldown = True
        return True