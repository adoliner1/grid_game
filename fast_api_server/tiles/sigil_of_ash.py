from .tile import Tile
from .. import game_utilities
from .. import game_constants

class SigilOfAsh(Tile):
    def __init__(self):
        super().__init__(
            name="Sigil of Ash",
            type="Scorer",
            number_of_slots=4,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "When one of your disciples is ^^burned^^, +2 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_cooldown": False,
                },
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "+3 points instead",
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
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        self.determine_influence()        
        ruler = self.determine_ruler(game_state)
        for player in [first_player, second_player]:
            player_influence = self.influence_per_player[player]
            if player_influence >= 3 and color == player:
                points_gained = 3 if player == ruler else 2
                game_state["points"][player] += points_gained
                await send_clients_log_message(f"{player} gains {points_gained} points from **{self.name}** due to their {color}_{disciple} being burned on {tile_burned_at.name}")