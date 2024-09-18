import game_utilities
import game_constants
from tiles.tile import Tile

class Prince(Tile):
    def __init__(self):
        super().__init__(
            name="Prince",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=7,
            description="At the __end of a round__, for each same-shape pair you have here, +1 point",
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,                    
                    "description": "At the __end of a round__, for each same-shape pair you have here, +3 additional points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                   
                },
            ]            
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        
        for color in ['red', 'blue']:
            shape_count = {'circle': 0, 'square': 0, 'triangle': 0}
            for slot in self.slots_for_shapes:
                if slot and slot["color"] == color:
                    shape_count[slot["shape"]] += 1
            
            pairs = sum(count // 2 for count in shape_count.values())
            
            base_points = pairs
            additional_points = 0
            
            if color == ruler and self.influence_per_player[color] >= self.influence_tiers[0]['influence_to_reach_tier']:
                additional_points = pairs * 3
            
            total_points = base_points + additional_points
            game_state["points"][color] += total_points
            
            if total_points > 0:
                await send_clients_log_message(f"{color} player earned {total_points} points ({base_points} base + {additional_points} additional) from {pairs} pairs of shapes on {self.name}")