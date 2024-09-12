import game_utilities
import game_constants
from tiles.tile import Tile

class Algebra(Tile):
    def __init__(self):
        super().__init__(
            name="Algebra",
            type="Producer",
            number_of_slots=5,
            minimum_power_to_rule=2,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "At the __start of a round__, ++produce++ 1 circle",
                    "is_on_cooldown": False,
                    "has_cooldown": False,
                },
                {
                    "power_to_reach_tier": 6,
                    "must_be_ruler": True,                     
                    "description": "++Produce++ another",
                    "is_on_cooldown": False,
                    "has_cooldown": False,
                }
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)    

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_power()
        if self.power_per_player[game_state['first_player']] >= self.power_tiers[0]['power_to_reach_tier']:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_state['first_player'], 1, 'circle', self.name, True)
        if self.power_per_player[game_utilities.get_other_player_color(game_state['second_player'])] >= self.power_tiers[0]['power_to_reach_tier']:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_state['second_player'], 1, 'circle', self.name, True)            

        ruler = self.determine_ruler(game_state)
        if (ruler == 'red' and self.power_per_player['red'] >= self.power_tiers[1]['power_to_reach_tier']):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, 'red', 1, 'circle', self.name, True)
        elif (ruler == 'blue' and self.power_per_player['blue'] >= self.power_tiers[1]['power_to_reach_tier']):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, 'blue', 1, 'circle', self.name, True)