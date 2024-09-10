import game_utilities
import game_constants
from tiles.tile import Tile

class Jupiter(Tile):
    def __init__(self):
        super().__init__(
            name="Jupiter",
            type="Producer/Scorer",
            minimum_power_to_rule=2,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 4,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your squares here to ++produce++ a triangle",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                     
                    "data_needed_for_use": [],
                },
                {
                    "power_to_reach_tier": 7,
                    "must_be_ruler": False,                    
                    "description": "**Action:** Same as above but ^^burn^^ one of your circles",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                     
                    "data_needed_for_use": [],
                },
            ] 
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        user = game_state["whose_turn_is_it"]

        if not self.power_tiers[0]['is_on_cooldown'] and self.power_per_player[user] >= 4 and any(slot and slot["shape"] == "square" and slot["color"] == user for slot in self.slots_for_shapes):
            useable_tiers.append(0)
        if not self.power_tiers[1]['is_on_cooldown'] and self.power_per_player[user] >= 7 and any(slot and slot["shape"] == "circle" and slot["color"] == user for slot in self.slots_for_shapes):
            useable_tiers.append(0)

        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        
        if self.power_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"{self.name} tier {tier_index} is on cooldown")
            return False
        
        if self.power_per_player[user] < self.power_tiers[tier_index]['power_to_reach_tier']:
            await send_clients_log_message(f"Not enough power on {self.name} to use tier {tier_index + 1}")
            return False
        
        index_of_jupiter = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        shape_to_burn = "square" if tier_index == 0 else "circle"
        slot_index_to_burn_shape_from = next((i for i, slot in enumerate(self.slots_for_shapes)
                                              if slot and slot["shape"] == shape_to_burn and slot["color"] == user), None)
        
        if slot_index_to_burn_shape_from is None:
            await send_clients_log_message(f"No {shape_to_burn} available to burn on {self.name}")
            return False
        
        await send_clients_log_message(f"Using {self.name} tier {tier_index}") 
        
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_jupiter, slot_index_to_burn_shape_from)
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, user, 1, 'triangle', self.name)
        
        self.power_tiers[tier_index]['is_on_cooldown'] = True
        return True