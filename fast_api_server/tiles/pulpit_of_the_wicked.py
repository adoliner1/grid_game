import game_utilities
import game_constants
from tiles.tile import Tile

class PulpitOfTheWicked(Tile):
    def __init__(self):
        super().__init__(
            name="Pulpit of the Wicked",
            type="Exile-Enhancer",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "Increase your exiling range by 2",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                    "leader_must_be_present": True, 
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_exiling_ranges(self, game_state):
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            if ruler == player and self.influence_per_player[player] >= self.influence_tiers[0]['influence_to_reach_tier'] and self.leaders_here[player]:
                game_state['exiling_range'][player] += 2