import game_utilities
import game_constants
from tiles.tile import Tile

class Calculus(Tile):
    def __init__(self):
        super().__init__(
            name="Calculus",
            type="Producer",
            minimum_power_to_rule=2,
            power_tiers=[
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": False,                    
                    "description": "At the __start of a round__, ++produce++ 1 square",
                    "is_on_cooldown": False,
                },
                {
                    "power_to_reach_tier": 8,
                    "must_be_ruler": True,                    
                    "description": "At the __start of a round__, ++produce++ 1 square",
                    "is_on_cooldown": False,
                },                
            ],
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_power()
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            if self.power_per_player[player] >= 5:
                await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, 1, 'square', self.name, True)
            if self.power_per_player[player] >= 8:
                await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, 1, 'square', self.name, True)
         