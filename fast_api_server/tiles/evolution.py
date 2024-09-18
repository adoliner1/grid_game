import game_utilities
import game_constants
from tiles.tile import Tile

class Evolution(Tile):
    def __init__(self):
        super().__init__(
            name="Evolution",
            type="power/Giver/Scorer",
            minimum_influence_to_rule=3,
            description=f"At the __end of a round__, ^^burn^^ each shape here and [[receive]] the next most powerful shape. Triangles yield circles",
            number_of_slots=7,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 0,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ 3 of your triangles here. +5 points and +5 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,   
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": [],
                },
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": True,                    
                    "description": "At the __end of the game__, -5 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                    
                },
            ]
        )

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        player_color = game_state["whose_turn_is_it"]
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "triangle")
        if triangle_count >= 3:
            useable_tiers.append(0)
        
        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player_color = game_action_container.whose_action
                
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Don't have enough triangles on {self.name}")
            return False

        await send_clients_log_message(f"Using {self.name}")

        for slot_index, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == player_color and slot["shape"] == "triangle":
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), slot_index)

        game_state['power'][player_color] += 5
        await send_clients_log_message(f"{player_color} gains 5 power from {self.name}")
        game_state["points"][player_color] += 5
        await send_clients_log_message(f"{player_color} gains 5 points from {self.name}")
        return True

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        await send_clients_log_message(f"Applying end of round effect for {self.name}")
        
        for i in range(len(self.slots_for_shapes)):
            if self.slots_for_shapes[i]:
                current_shape = self.slots_for_shapes[i]["shape"]
                player_color = self.slots_for_shapes[i]["color"]
                
                # Burn the current shape
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), i)
                
                # Produce the next most influenceful shape
                if current_shape == "circle":
                    new_shape = "square"
                elif current_shape == "square":
                    new_shape = "triangle"
                else:  # triangle
                    new_shape = "circle"
                
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, self, new_shape)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} deducts 5 points from {ruler}")
            game_state["points"][ruler] -= 5