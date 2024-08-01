import game_utilities

class Powerup:
    def __init__(self, name, description, number_of_slots, owner, listener_type=None, data_needed_for_use=[], is_on_cooldown=False):
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

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "slots_for_shapes": self.slots_for_shapes,
            "is_on_cooldown": self.is_on_cooldown
        } 
    
    def set_available_actions_for_use(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def set_available_client_actions_for_reaction(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
class ProduceCircleFor3Circles(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Produce Circle For 3 Circles",
            description = "If filled with circles, produce 1 circle at the start of the round",
            number_of_slots=3,
            owner=owner
        )

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot["shape"] == "circle":
                    circle_count += 1
        if circle_count == 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, "circle", self.name)

class BurnTwoCirclesProduceTriangle(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Burn Two Circles Place Square",
            description = "If filled with circles, you may burn 2 circles here to produce a triangle",
            number_of_slots=5,
            owner=owner
        )

    def is_useable(self, game_state):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "circle":
                circle_count += 1

        return circle_count == 5
    
    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):    
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Not enough circles on {self.name} to use it")
            return False
        
        await game_utilities.burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, game_utilities.find_index_of_powerup_by_name(game_state, self.name), self.number_of_slots-1)
        await game_utilities.burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, game_utilities.find_index_of_powerup_by_name(game_state, self.name), self.number_of_slots-2)
        await send_clients_log_message(f"{self.name} is used")
        
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, 'triangle', self.name)
        return True

class ProduceTriangleFor3Squares(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Produce Triangle For 3 Squares",
            description = "If filled with squares, produce 1 triangle at the start of the round",
            number_of_slots=3,
            owner=owner
        )

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        square_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot["shape"] == "square":
                    square_count += 1
        if square_count == 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, "square", self.name)