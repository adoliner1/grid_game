import game_utilities
import game_constants
from tiles.tile import Tile

class King(Tile):
    def __init__(self):
        super().__init__(
            name="King",
            type="Scorer",
            minimum_influence_to_rule=3,
            influence_tiers=[],
            description="At the end of the game:\n+3 influence differential, +4 points\n+7 influence differential, +15 points instead",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_influence()
        red_influence = self.influence_per_player['red']
        blue_influence = self.influence_per_player['blue']
        influence_differential = abs(red_influence - blue_influence)
        
        if influence_differential >= 7:
            points_to_add = 15
        elif influence_differential >= 3:
            points_to_add = 4
        else:
            points_to_add = 0

        if points_to_add > 0:
            winner = 'red' if red_influence > blue_influence else 'blue'
            await send_clients_log_message(f"influence differential on **{self.name}** is {influence_differential} in favor of {winner}")
            game_state["points"][winner] += points_to_add
        else:
            await send_clients_log_message(f"influence differential on **{self.name}** is less than 3, no points awarded")