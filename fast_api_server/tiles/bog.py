import game_utilities
import game_constants
from tiles.tile import Tile

class Bog(Tile):
    def __init__(self):
        super().__init__(
            name="Bog",
            type="Swamp",
            minimum_influence_to_rule=1,
            description = f"",
            number_of_slots=1,
            influence_tiers={
                "influence_to_reach_tier": 1,
                "must_be_ruler": True,                    
                "description": "At the __end of the game__, -3 points",
                "is_on_cooldown": False,
                "leader_must_be_present": False, 
                "has_a_cooldown": False,
            },      
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)
    
    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            points_to_lose = 3
            game_state['points'][ruler] -= points_to_lose
            await send_clients_log_message(f"{ruler} loses {points_to_lose} points from **{self.name}**")