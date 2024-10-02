import game_utilities
import game_constants
from tiles.tile import Tile

class FieldsOfTheFaithful(Tile):
    def __init__(self):
        super().__init__(
            name="Fields of the Faithful",
            type="Recruitment-Enhancer",
            minimum_influence_to_rule=4,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 8,
                    "must_be_ruler": True,
                    "description": "Reduce your recruiting costs by 1",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                    "leader_must_be_present": False, 
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_recruiting_costs(self, game_state):
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            if ruler == player and self.influence_per_player[player] >= self.influence_tiers[0]['influence_to_reach_tier']:
                for disciple in game_state['recruiting_costs'][ruler]:
                    game_state['recruiting_costs'][ruler][disciple] -= 1