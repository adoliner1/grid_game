import game_utilities
import game_constants
from tiles.tile import Tile

class King(Tile):
    def __init__(self):
        super().__init__(
            name="King",
            type="Scorer",
            description="At the end of the game\n+3 power differential, +4 points\n+7 power differential, +15 points instead\nRuler: Most Power, minimum 3",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        red_power = self.power_per_player["red"]
        blue_power = self.power_per_player["blue"]
       
        if red_power > blue_power and red_power >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_power > red_power and blue_power >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler is not None:
            power_differential = self.power_per_player[ruler] - self.power_per_player[game_utilities.get_opponent_color(ruler)]
            
            if power_differential >= 7:
                points_to_add = 15
            elif power_differential >= 3:
                points_to_add = 4
            else:
                points_to_add = 0

            if points_to_add > 0:
                await send_clients_log_message(f"{self.name} gives {points_to_add} points to {ruler}")
                game_state["points"][ruler] += points_to_add