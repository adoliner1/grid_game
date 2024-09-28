import game_utilities
import game_constants
from tiles.tile import Tile

class SoulForge(Tile):
    def __init__(self):
        super().__init__(
            name="Soul Forge",
            type="Generator",
            number_of_slots=5,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "After one of your disciples is ^^burned^^, +1 power",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_cooldown": False,
                },
            ]
        )
 
    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')
        tile_burned_at = game_state['tiles'][index_of_tile_burned_at]
        color = data.get('color')
        disciple = data.get('disciple')
        self.determine_influence()        
        ruler = self.determine_ruler(game_state)
        player_influence = self.influence_per_player[color]

        if player_influence >= self.influence_tiers[0]['influence_to_reach_tier'] and color == ruler:
            power_gained = 1
            game_state["power"][color] += power_gained
            await send_clients_log_message(f"{color} gains {power_gained} power from **{self.name}** due to their {disciple} being burned on {tile_burned_at.name}")