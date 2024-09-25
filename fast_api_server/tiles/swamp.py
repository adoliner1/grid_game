import game_utilities
import game_constants
from tiles.tile import Tile

class Swamp(Tile):
    def __init__(self):
        super().__init__(
            name="Swamp",
            type="",
            minimum_influence_to_rule=1,
            description = f"",
            number_of_slots=1,         
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)