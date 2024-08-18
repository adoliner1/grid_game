import game_utilities
import game_constants

class Tile:
    def __init__(self, name, description, number_of_slots, data_needed_for_use=[], is_on_cooldown=False):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.ruler = None
        self.data_needed_for_use = data_needed_for_use
        self.is_on_cooldown=is_on_cooldown
        self.red_power = 0
        self.blue_power = 0

    def determine_ruler(self, game_state):
        pass

    def is_useable(self, game_state):
        return False

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, player_color, **kwargs):
        pass
 
    def set_available_actions_for_use(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def set_available_actions_for_reaction(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "red_power": self.red_power,
            "blue_power": self.blue_power,
            "slots_for_shapes": self.slots_for_shapes,
            "ruler": self.ruler,
            "is_on_cooldown": self.is_on_cooldown
        } 