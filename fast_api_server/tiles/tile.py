from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile

class Tile:
    def __init__(self, name, description, number_of_slots, data_needed_for_use=[]):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.ruler = None
        self.data_needed_for_use = data_needed_for_use

    def determine_ruler(self, game_state):
        pass

    def is_useable(self, game_state):
        return False

    async def start_of_round_effect(self, game_state, callback):
        pass

    async def end_of_round_effect(self, game_state, callback):
        pass

    async def end_of_game_effect(self, game_state, callback):
        pass

    async def place_shape_at_index(self, game_state, index, shape, color, callback):
        self.slots_for_shapes[index] = {'shape': shape, 'color': color}
        await callback(f"{color} placed a {shape} on {self.name}")

    async def use_tile(self, game_state, player_color, callback, **kwargs):
        pass

    async def move_shape_from_one_tile_to_another(self, game_state, source_slot_index, source_tile_index, destination_slot_index, destination_tile_index, callback):
        pass

    async def burn_shape_at_index(self, game_state, slot_index, callback):
        shape = self.slots_for_shapes[slot_index]["shape"]
        self.slots_for_shapes[slot_index] = None
        await callback(f"burning {shape} at {self.name}")

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "slots_for_shapes": self.slots_for_shapes,
            "ruler": self.ruler,
        } 
    
    def set_available_actions(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details