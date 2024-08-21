import game_utilities
import game_constants
from tiles.tile import Tile

class Algebra(Tile):
    def __init__(self):
        super().__init__(
            name="Algebra",
            type="Producer",
            description = f"3 power: At the start of a round, produce 1 circle\n Ruler: Most power, minimum 5, produce another",
            number_of_slots=3,
        )

    def determine_ruler(self, game_state):
        self.determine_power()

        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 5:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 5:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.determine_power()

        if self.power_per_player[game_state['first_player']] >= 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'circle', self.name)
        if self.power_per_player[game_utilities.get_other_player_color(game_state['first_player'])] >= 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'circle', self.name)            

        ruler = self.determine_ruler(game_state)
        if (ruler == 'red'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'circle', self.name)
        elif (ruler == 'blue'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'circle', self.name)