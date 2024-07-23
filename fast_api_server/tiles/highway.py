from game_utilities import *
from tiles.tile import Tile

class Highway(Tile):
    def __init__(self):
        super().__init__(
            name="Highway",
            description=f"Ruling Criteria: 3 or more shapes\nRuling Benefits: Once per turn, burn a shape here to move a shape on a tile to an empty slot.",
            number_of_slots=5,
            data_needed_for_use=["slot_to_burn_shape_from", "slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it and not self.is_on_cooldown

    def set_available_actions(self, game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        if current_piece_of_data_to_fill_in_current_action == "slot_to_burn_shape_from":
            slots_with_a_shape = get_slots_with_a_shape_of_player_color_at_tile_index(game_state, self.determine_ruler(game_state), current_action["index_of_tile_in_use"])
            available_actions_with_details["select_a_slot"] = {current_action["index_of_tile_in_use"]: slots_with_a_shape}
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_from":
            slots_with_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions_with_details["select_a_slot"] = slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_to":
            slots_without_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if not slot:
                        slots_without_shapes.append(slot_index)
                if slots_without_shapes:
                    slots_without_a_shape[index] = slots_without_shapes
            available_actions_with_details["select_a_slot"] = slots_without_a_shape

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

        slot_to_burn_shape_from = kwargs.get('slot_to_burn_shape_from').get('slot_index')
        index_of_tile_to_burn_shape_from = kwargs.get('slot_to_burn_shape_from').get('tile_index')
        slot_to_move_shape_from = kwargs.get('slot_and_tile_to_move_shape_from').get('slot_index')
        index_of_tile_to_move_shape_from = kwargs.get('slot_and_tile_to_move_shape_from').get('tile_index')
        slot_to_move_shape_to = kwargs.get('slot_and_tile_to_move_shape_to').get('slot_index')
        index_of_tile_to_move_shape_to = kwargs.get('slot_and_tile_to_move_shape_to').get('tile_index')
        shape_to_move = game_state['tiles'][index_of_tile_to_move_shape_from].slots_for_shapes[slot_to_move_shape_from]["shape"]
        index_of_highway = find_index_of_tile_by_name(game_state, self.name)

        if game_state["tiles"][index_of_tile_to_burn_shape_from].slots_for_shapes[slot_to_burn_shape_from] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to burn from {game_state['tiles'][index_of_tile_to_burn_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_burn_shape_from].slots_for_shapes[slot_to_burn_shape_from]["color"] != self.ruler:
            await callback(f"Tried to use {self.name} but chose a shape that didn't belong to them for burning")
            return False
        
        if index_of_tile_to_burn_shape_from != index_of_highway:
            await callback(f"Tried to use {self.name} but chose a tile other than {self.name} to burn the shape")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_from].slots_for_shapes[slot_to_move_shape_from] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_to].slots_for_shapes[slot_to_move_shape_to] != None:
            await callback(f"Tried to use {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_shape_to].name}")
            return False
        
        if slot_to_burn_shape_from == slot_to_move_shape_from:
            await callback(f"{self.name} can't move the shape that was burned")
            return False            

        await callback(f"Using {self.name}")
        await self.burn_shape_at_index(game_state, slot_to_burn_shape_from, callback)
        move_shape(game_state, index_of_tile_to_move_shape_from, slot_to_move_shape_from, index_of_tile_to_move_shape_to, slot_to_move_shape_to)
        await callback(f"Moved {shape_to_move} from {game_state['tiles'][index_of_tile_to_move_shape_from].name} to {game_state['tiles'][index_of_tile_to_move_shape_to].name}")
        return True