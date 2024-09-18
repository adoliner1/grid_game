import game_utilities
import game_constants
from tiles.tile import Tile

class Nitrogen(Tile):
    def __init__(self):
        super().__init__(
            name="Nitrogen",
            type="Giver/Power-Creator",
            minimum_influence_to_rule=3,
            description="At the __end of a round__, for each triangle you have here, [[receive]] a square and a circle here",
            number_of_slots=11,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 0,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your sets here for +5 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "leader_must_be_present": False,                      
                    "data_needed_for_use": [],
                },            
            ]
        )

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == whose_turn_is_it)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == whose_turn_is_it)
        
        if circle_count >= 1 and square_count >= 1 and triangle_count >= 1:
            useable_tiers.append(0)

        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"{self.name} runs")

        for player in [first_player, second_player]:
            triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player and slot["shape"] == "triangle")
            
            for _ in range(triangle_count):
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, self, 'square')
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, self, 'circle')
            
    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == player)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == player)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == player)
        
        if circle_count < 1 or square_count < 1 or triangle_count < 1:
            await send_clients_log_message(f"Not enough shapes to burn a set on {self.name}")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        nitrogen_tile_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        shapes_burned = {'circle': 0, 'square': 0, 'triangle': 0}
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == player and shapes_burned[slot["shape"]] < 1:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, nitrogen_tile_index, i)
                shapes_burned[slot["shape"]] += 1
                if all(count == 1 for count in shapes_burned.values()):
                    break
        
        await send_clients_log_message(f"{player} burns a set on {self.name}")
        
        power_to_gain = 5
        game_state["power"][player] += power_to_gain
        await send_clients_log_message(f"{player} gains {power_to_gain} power from burning a set on {self.name}")

        return True