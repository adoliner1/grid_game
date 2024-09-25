import game_utilities
import game_constants
from tiles.tile import Tile

class Zeal(Tile):
    def __init__(self):
        super().__init__(
            name="Zeal",
            type="Recruitment-Enhancer",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "Increase your recruitment range by 1",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                    "leader_must_be_present": False, 
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_recruiting_ranges(self, game_state):
        ruler = self.determine_ruler(game_state)
        if ruler and self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']:
            game_state['recruiting_range'][ruler] += 1