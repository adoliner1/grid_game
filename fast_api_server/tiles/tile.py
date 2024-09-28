import game_utilities
import game_constants

class Tile:
    def __init__(self, name, type, number_of_slots, influence_tiers=[], minimum_influence_to_rule=0, description=None, data_needed_for_use=[], is_on_cooldown=False, disciples_which_can_be_recruited_to_this=["follower", "acolyte", "sage"], TILE_PRIORITY=0):
        self.name = name
        self.type = type
        self.description = description
        self.influence_tiers = influence_tiers
        self.number_of_slots = number_of_slots
        self.minimum_influence_to_rule = minimum_influence_to_rule
        self.slots_for_disciples = [None] * number_of_slots
        self.influence_modifiers = []
        self.ruler = None
        self.influence_per_player = {"red": 0, "blue": 0}
        self.disciples_which_can_be_recruited_to_this=disciples_which_can_be_recruited_to_this
        self.leaders_here = {"red": False, "blue": False}
        self.TILE_PRIORITY = TILE_PRIORITY

    def determine_ruler(self, game_state, minimum_influence_needed_to_rule=0):
        self.determine_influence()
        if self.influence_per_player["red"] > self.influence_per_player["blue"] and self.influence_per_player["red"] >= minimum_influence_needed_to_rule:
            self.ruler = 'red'
            return 'red'
        elif self.influence_per_player["blue"] > self.influence_per_player["red"] and self.influence_per_player["blue"] >= minimum_influence_needed_to_rule:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def determine_influence(self):
        new_influence_per_player = {"red": 0, "blue": 0}

        for slot in self.slots_for_disciples:
            if slot is not None:
                color = slot["color"]
                disciple = slot["disciple"]
                new_influence_per_player[color] += game_constants.disciple_influence[disciple]

        # Apply influence modifiers
        for modifier in self.influence_modifiers:
            affected_color = modifier["affected_color"]
            amount_of_influence = modifier["amount_of_influence"]
            new_influence_per_player[affected_color] += amount_of_influence

        for color in game_constants.player_colors:
            if self.leaders_here[color]:
                new_influence_per_player[color] += game_constants.leader_influence
         
        # Set the calculated influence
        self.influence_per_player = new_influence_per_player

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
    
    def modify_recruiting_ranges(self, game_state):
        pass

    def modify_expected_incomes(self, game_state):
        pass

    def modify_recruiting_costs(self, game_state):
        pass

    def modify_movement_ranges(self, game_state):
        pass

    def modify_exiling_ranges(self, game_state):
        pass

    def modify_exiling_costs(self, game_state):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "type": self.type,
            "influence_tiers": self.influence_tiers,
            "minimum_influence_to_rule": self.minimum_influence_to_rule,
            "description": self.description,
            "influence_per_player": self.influence_per_player,
            "leaders_here": self.leaders_here,
            "slots_for_disciples": self.slots_for_disciples,
            "ruler": self.ruler,
        }