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
                    "power_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "At the __start of a round__, +3 stamina",
                    "is_on_cooldown": False,
                },              
            ],
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_power()
        ruler = self.determine_ruler(game_state)
        if ruler: 
            await send_clients_log_message(f'{self.name} gives 3 to {ruler}')  
            game_state['stamina'][ruler] += 3