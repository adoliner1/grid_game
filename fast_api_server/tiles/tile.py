import game_utilities
import game_constants

class Tile:
    def __init__(self, name, type, description, number_of_slots, data_needed_for_use=[], is_on_cooldown=False):
        self.name = name
        self.type = type
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.power_modifiers = []
        self.ruler = None
        self.data_needed_for_use = data_needed_for_use
        self.is_on_cooldown=is_on_cooldown
        self.power_per_player = {"red": 0, "blue": 0}

    def determine_ruler(self, game_state):
        pass

    def determine_power(self):
        # Initialize power for both colors
        new_power_per_player = {"red": 0, "blue": 0}

        # Calculate power from shapes
        for slot in self.slots_for_shapes:
            if slot is not None:
                color = slot["color"]
                shape = slot["shape"]
                new_power_per_player[color] += game_constants.shape_power[shape]

        # Apply power modifiers
        for modifier in self.power_modifiers:
            affected_color = modifier["affected_color"]
            amount_of_power = modifier["amount_of_power"]
            new_power_per_player[affected_color] += amount_of_power

        # Set the calculated power
        self.power_per_player = new_power_per_player

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
            "type": self.type,
            "description": self.description,
            "power_per_player": self.power_per_player,
            "slots_for_shapes": self.slots_for_shapes,
            "ruler": self.ruler,
            "is_on_cooldown": self.is_on_cooldown
        } 