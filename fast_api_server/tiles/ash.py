import game_utilities
import game_constants
from tiles.tile import Tile

class Ash(Tile):
    def __init__(self):
        super().__init__(
            name="Ash",
            type="Scorer",
            number_of_slots=5,
            minimum_power_to_rule=2,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "After any shape is ^^burned^^ on a tile, if you're present there, +2 points",
                    "is_on_cooldown": False,
                    "has_cooldown": False,
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "+3 points instead",
                    "is_on_cooldown": False,
                    "has_cooldown": False,
                },
            ]
        )
 
    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        ruler = self.determine_ruler(game_state)
       
        for player in [first_player, second_player]:
            player_power = self.power_per_player[player]
            if player_power >= 3 and game_utilities.has_presence(game_state["tiles"][index_of_tile_burned_at], player):
                points_gained = 3 if player == ruler else 2
                game_state["points"][player] += points_gained
                await send_clients_log_message(f"{player} gains {points_gained} points from {self.name} due to a shape being burned on {game_state['tiles'][index_of_tile_burned_at].name}")