from game_utilities import *
from tiles.tile import Tile

class TeleportingCabinet(Tile):
    def __init__(self):
        super().__init__(
            name="Teleporting Cabinet",
            description=f"Ruling Criteria: 3 or more shapes\nRuling Benefits: Once per turn, choose a shape at an adjacent tile and swap it with a shape anywhere.",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_swap_shape_from", "slot_and_tile_to_swap_shape_to"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it and not self.is_on_cooldown

    def set_available_actions(self, game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_swap_shape_from":
            adjacent_slots_with_a_shape = {}
            indices_of_adjacent_tiles = get_adjacent_tile_indices(current_action["index_of_tile_in_use"])
            for index in indices_of_adjacent_tiles:
                slots_with_shapes = []
                for slot_index, slot in enumerate(game_state["tiles"][index].slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    adjacent_slots_with_a_shape[index] = slots_with_shapes
            available_actions_with_details["select_a_slot"] = adjacent_slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_swap_shape_to":
            slots_with_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions_with_details["select_a_slot"] = slots_with_a_shape

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

    async def use_tile(self, game_state, player_color, callback, **kwargs):
        self.determine_ruler(game_state)
        if not self.ruler:
            await callback(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != player_color:
            await callback(f"Non-ruler tried to use {self.name}")
            return False

        index_of_cabinet = find_index_of_tile_by_name(game_state, self.name)
        slot_to_swap_shape_from = kwargs.get('slot_and_tile_to_swap_shape_from').get('slot_index')
        index_of_tile_to_swap_shape_from = kwargs.get('slot_and_tile_to_swap_shape_from').get('tile_index')
        slot_to_swap_shape_to = kwargs.get('slot_and_tile_to_swap_shape_to').get('slot_index')
        index_of_tile_to_swap_shape_to = kwargs.get('slot_and_tile_to_swap_shape_to').get('tile_index')

        if not determine_if_directly_adjacent(index_of_cabinet, index_of_tile_to_swap_shape_from):
            await callback(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False

        if game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_to_swap_shape_from] is None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to swap from {game_state['tiles'][index_of_tile_to_swap_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_to_swap_shape_to] is None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to swap to {game_state['tiles'][index_of_tile_to_swap_shape_to].name}")
            return False

        slot_data_to_swap_from = game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_to_swap_shape_from]
        slot_data_to_swap_to = game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_to_swap_shape_to]

        await callback(f"Using {self.name}")

        # Swap shapes
        game_state["tiles"][index_of_tile_to_swap_shape_from].slots_for_shapes[slot_to_swap_shape_from] = slot_data_to_swap_to
        game_state["tiles"][index_of_tile_to_swap_shape_to].slots_for_shapes[slot_to_swap_shape_to] = slot_data_to_swap_from

        await callback(f"Swapped {slot_data_to_swap_from['shape']} from {game_state['tiles'][index_of_tile_to_swap_shape_from].name} with {slot_data_to_swap_to['shape']} at {game_state['tiles'][index_of_tile_to_swap_shape_to].name}")
        self.is_on_cooldown = True
        return True