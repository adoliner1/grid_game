import game_utilities
import game_constants
from tiles.tile import Tile

class Calculus(Tile):
    def __init__(self):
        super().__init__(
            name="Calculus",
            type="Producer",
            description="**5 power:** At the __start of a round__, ++produce++ 1 square\n**Ruler, Most Power, Minimum 8:** ++Produce++ another",
            number_of_slots=
            5,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 8:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 8:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.determine_power()
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            if self.power_per_player[player] >= 5:
                await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player, 1, 'square', self.name, True)

        ruler = self.determine_ruler(game_state)
        if ruler:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, 1, 'square', self.name, True)