import game_utilities
import game_constants
from tiles.tile import Tile

class KingsCourt(Tile):
    def __init__(self):
        super().__init__(
            name="King's Court",
            type="Scorer",
            minimum_influence_to_rule= 6,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "At the __end of the game__, +5 points per tile you rule",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,       
                    "leader_must_be_present": False,              
                    "data_needed_for_use": []
                },
            ],
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_expected_incomes(self, game_state):
        if game_state['round'] != 5:
            return
        
        game_utilities.determine_rulers(game_state)
        if self.ruler:
            tiles_ruled = 0
            for tile in game_state['tiles']:
                if tile.ruler == self.ruler:
                    tiles_ruled += 1

            points_to_gain = 5*tiles_ruled
            game_state['expected_points_incomes'][self.ruler] += points_to_gain

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_utilities.determine_rulers(game_state)
        if self.ruler:
            tiles_ruled = 0
            for tile in game_state['tiles']:
                if tile.ruler == self.ruler:
                    tiles_ruled += 1

            points_to_gain = 5*tiles_ruled
            game_state['points'][self.ruler] += points_to_gain
            await send_clients_log_message(f"{self.ruler} rules {self.name} and {tiles_ruled} tiles. They gain {points_to_gain} points")