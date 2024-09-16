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
                    "description": "At the __start of a round__, +1 stamina",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_cooldown": False,
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": True,                     
                    "description": "At the __start of a round__, +1 stamina",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_cooldown": False,
                }
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)    

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_power()
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            stamina_to_gain = 0
            if self.power_per_player[player] >= self.power_tiers[0]['power_to_reach_tier']:
                stamina_to_gain += 1
            if ruler == player:
                stamina_to_gain += 1
            
            if stamina_to_gain > 0:
                await send_clients_log_message(f'{self.name} gives {stamina_to_gain} to {player}')  
                game_state['stamina'][player] += stamina_to_gain