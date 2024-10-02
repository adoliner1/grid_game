import game_utilities
import game_constants
from tiles.tile import Tile

class LilyPad(Tile):
    def __init__(self):
        super().__init__(
            name="Lily Pad",
            type="Generator",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "When you move on to Lily Pad, +1 power (this will trigger if you become ruler as you move here)",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,   
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": [],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_leader_move"][self.name] = self.on_leader_move_effect

    async def on_leader_move_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        color = data.get('leader_color_moved')
        if self.determine_ruler(game_state) == color:
            power_to_gain = 1
            game_state['power'][color] += power_to_gain
            await send_clients_log_message(f"{color} gains {power_to_gain} power for moving on to **{self.name}**")