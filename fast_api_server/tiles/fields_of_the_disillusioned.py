import asyncio
import game_action_container
from tile import Tile
import game_utilities
import game_constants

class FieldsOfTheDisillusioned(Tile):
    def __init__(self):
        super().__init__(
            name="Fields of the Disillusioned",
            type="Exile-Enhancer",
            minimum_influence_to_rule=4,
            number_of_slots=4,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "Reduce your ++exiling++ costs by 1",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                    "leader_must_be_present": False, 
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_exiling_costs(self, game_state):
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            if ruler == player and self.influence_per_player[player] >= self.influence_tiers[0]['influence_to_reach_tier']:
                for disciple in game_state['exiling_costs'][ruler]:
                    game_state['exiling_costs'][ruler][disciple] -= 1