import game_utilities
import game_constants
from tiles.tile import Tile

class Waterfalls(Tile):
    def __init__(self):
        super().__init__(
            name="Waterfalls",
            type="Scorer",
            description="3 Power: At the end of a round, +1 point per tile you're present at\n6 Power: +2 points instead\nRuler: Most Power",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"]:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"]:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            player_power = self.power_per_player[player]
            if player_power >= 3:
                tiles_present_at = 0
                for tile in game_state["tiles"]:
                    if game_utilities.has_presence(tile, player):
                        tiles_present_at += 1

                points_per_tile = 2 if player_power >= 6 else 1
                points_awarded = tiles_present_at * points_per_tile

                game_state["points"][player] += points_awarded
                await send_clients_log_message(f"{player} gains {points_awarded} points from {self.name} for being present at {tiles_present_at} tiles with {player_power} power")