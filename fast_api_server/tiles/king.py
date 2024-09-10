import game_utilities
import game_constants
from tiles.tile import Tile

class King(Tile):
    def __init__(self):
        super().__init__(
            name="King",
            type="Scorer",
            minimum_power_to_rule=3,
            power_tiers=[],
            description="At the end of the game:\n**+3 power differential**, +4 points\n**+7 power differential**, +15 points instead",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.determine_power()
        red_power = self.power_per_player['red']
        blue_power = self.power_per_player['blue']
        power_differential = abs(red_power - blue_power)
        
        if power_differential >= 7:
            points_to_add = 15
        elif power_differential >= 3:
            points_to_add = 4
        else:
            points_to_add = 0

        if points_to_add > 0:
            winner = 'red' if red_power > blue_power else 'blue'
            await send_clients_log_message(f"Power differential on {self.name} is {power_differential} in favor of {winner}")
            game_state["points"][winner] += points_to_add
        else:
            await send_clients_log_message(f"Power differential on {self.name} is less than 3, no points awarded")