import game_utilities
import game_constants
from tiles.tile import Tile

class Carbon(Tile):
    def __init__(self):
        super().__init__(
            name="Carbon",
            type="Giver/Scorer",
            description="At the __end of a round__, for each circle you have here, [[receive]] another circle here",
            number_of_slots=9,
            minimum_power_to_rule=1,            
            power_tiers=[
                {
                    "power_to_reach_tier": 0,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ 3 of your circles here to [[receive]] a triangle here",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "data_needed_for_use": [],
                },
                {
                    "power_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "**Action:** ^^Burn^^ 3 of your circles here to [[receive]] a triangle here. +3 points if you do.",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "data_needed_for_use": [],
                },                
            ]      
        )

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        number_of_circles_current_player_has_here = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it)
        ruler = self.determine_ruler(game_state)

        if number_of_circles_current_player_has_here >= 3:
            useable_tiers.append(0)
            if ruler == whose_turn_is_it and self.power_per_player[whose_turn_is_it] >= 6:
                useable_tiers.append(1)

        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        first_player_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == first_player and slot["shape"] == "circle")
        second_player_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == second_player and slot["shape"] == "circle")

        for _ in range(first_player_count):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, first_player, self, 'circle')

        for _ in range(second_player_count):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, second_player, self, 'circle')

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == player)
        
        if circle_count < 3:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False

        if tier_index == 1:
            ruler = self.determine_ruler(game_state)
            if player != ruler or self.power_per_player[player] < 6:
                await send_clients_log_message(f"Cannot use tier 1 of {self.name}. Must be ruler with at least 6 power.")
                return False
        
        await send_clients_log_message(f"{self.name} tier {tier_index} is used")
        circles_burned = 0
        for index, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "circle" and slot["color"] == player:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), index)
                circles_burned += 1
                if circles_burned == 3:
                    break

        if circles_burned < 3:
            await send_clients_log_message(f"Not enough circles were burned on {self.name}")
            return False
        
        await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player, self, 'triangle')
        
        if tier_index == 1:
            game_state["points"][player] += 3
            await send_clients_log_message(f"{player} gains 3 points from using tier 1 of {self.name}")

        return True