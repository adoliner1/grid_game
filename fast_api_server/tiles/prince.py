import game_utilities
import game_constants
from tiles.tile import Tile

class Prince(Tile):
    def __init__(self):
        super().__init__(
            name="Prince",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=6,
            description="At the __end of each round__, for each same-disciple pair you have here, +2 points",
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "+3 points per pair instead",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,
                },
            ]            
        )

    def modify_expected_incomes(self, game_state):
        ruler = self.determine_ruler(game_state)
        
        for color in ['red', 'blue']:
            disciple_count = {'follower': 0, 'acolyte': 0, 'sage': 0}
            for slot in self.slots_for_disciples:
                if slot and slot["color"] == color:
                    disciple_count[slot["disciple"]] += 1
            
            pairs = sum(count // 2 for count in disciple_count.values())
            if color == ruler and self.influence_per_player[color] >= self.influence_tiers[0]['influence_to_reach_tier']:
                points_to_gain = pairs*3
            else:
                points_to_gain = pairs*2
            
            game_state["expected_points_incomes"][color] += points_to_gain

                
    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        
        for color in ['red', 'blue']:
            disciple_count = {'follower': 0, 'acolyte': 0, 'sage': 0}
            for slot in self.slots_for_disciples:
                if slot and slot["color"] == color:
                    disciple_count[slot["disciple"]] += 1
            
            pairs = sum(count // 2 for count in disciple_count.values())
            if color == ruler and self.influence_per_player[color] >= self.influence_tiers[0]['influence_to_reach_tier']:
                points_to_gain = pairs*3
            else:
                points_to_gain = pairs*2
            
            game_state["points"][color] += points_to_gain
            
            if points_to_gain > 0:
                await send_clients_log_message(f"{color} earned {points_to_gain} points for {pairs} pairs of disciples on **{self.name}**")