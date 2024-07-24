from game_utilities import *

class Powerup:
    def __init__(self, name, description, number_of_slots, owner, listener_type=None, data_needed_for_use=None, is_on_cooldown=False):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.owner = owner
        self.listener_type = listener_type
        self.data_needed_for_use = data_needed_for_use
        self.is_on_cooldown=is_on_cooldown

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

    async def use_powerup(self, game_state, player_color, callback, **kwargs):
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
            "is_on_cooldown": self.is_on_cooldown
        } 
    
    def set_available_actions(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
class ProduceCircleFor3Circles(Powerup):
    def __init__(self):
        super().__init__(
            name = "Produce Circle For 3 Circles",
            description = "If filled with circles, produce 1 circle at the start of the round",
            number_of_slots=3,
        )

    async def start_of_round_effect(self, game_state, callback):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot["shape"] == "circle":
                    circle_count += 1
        if circle_count == 3:
            produce_shape_for_player(game_state, self.owner, 1, "circle", self.name, callback=None)

class BurnTwoCirclesPlaceSquare(Powerup):
    def __init__(self):
        super().__init__(
            name = "Burn Two Circles Place Square",
            description = "If filled with circles, you may burn 2 circles here and lose 2 points to place a square",
            number_of_slots=4,
        )

    def is_useable(self, game_state):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "circle":
                circle_count += 1

        return circle_count == 4
    
    async def use_powerup(self, game_state, callback, **kwargs):    
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle")
        
        if circle_count != 4:
            await callback(f"Not enough circles to on {self.name} to use it")
            return False
        
        await self.burn_shape_at_index(game_state, self.number_of_slots-1, callback)
        await self.burn_shape_at_index(game_state, self.number_of_slots-2, callback)
        await callback(f"{self.name} is used")
        
        await produce_shape_for_player(game_state, player_color, 1, 'triangle', self.name, callback)
        return True
