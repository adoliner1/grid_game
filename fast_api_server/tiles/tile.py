import game_utilities
import game_constants

class Tile:
    def __init__(self, name, type, number_of_slots, power_tiers=[], minimum_power_to_rule=0, description=None, data_needed_for_use=[], is_on_cooldown=False, shapes_which_can_be_recruited_to_this=["circle", "square", "triangle"]):
        self.name = name
        self.type = type
        self.description = description
        self.power_tiers = power_tiers
        self.number_of_slots = number_of_slots
        self.minimum_power_to_rule = minimum_power_to_rule
        self.slots_for_shapes = [None] * number_of_slots
        self.power_modifiers = []
        self.ruler = None
        self.power_per_player = {"red": 0, "blue": 0}
        self.shapes_which_can_be_recruited_to_this=shapes_which_can_be_recruited_to_this
        self.leaders_here = {"red": False, "blue": False}

    def determine_ruler(self, game_state, minimum_power_needed_to_rule=0):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= minimum_power_needed_to_rule:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= minimum_power_needed_to_rule:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def determine_power(self):
        new_power_per_player = {"red": 0, "blue": 0}

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

        for color in game_constants.player_colors:
            if self.leaders_here[color]:
                new_power_per_player[color] += game_constants.leader_power
         
        # Set the calculated power
        self.power_per_player = new_power_per_player

    def is_useable(self, game_state):
        return False
    
    def get_useable_tiers(self, game_state):
        return []
    
    def create_action_container(self, tier):
        pass

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def use_a_tier(self, tier, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, player_color, **kwargs):
        pass
 
    def set_available_actions_for_use(game_state, tier_index ,current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def set_available_actions_for_reaction(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def serialize(self):
        return {
            "name": self.name,
            "type": self.type,
            "power_tiers": self.power_tiers,
            "minimum_power_to_rule": self.minimum_power_to_rule,
            "description": self.description,
            "power_per_player": self.power_per_player,
            "leaders_here": self.leaders_here,
            "slots_for_shapes": self.slots_for_shapes,
            "ruler": self.ruler,
        } 