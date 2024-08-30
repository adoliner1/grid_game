import game_utilities
import game_constants
from tiles.tile import Tile

class Ash(Tile):
    def __init__(self):
        super().__init__(
            name="Ash",
            type="Scorer",
            description="**3 Power:** After any shape is ^^burned^^ on a tile, if you're present there, +2 points\n**5 Power:** +3 points instead\n**Ruler: Most Power**",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"]:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"]:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        ruler = self.determine_ruler(game_state)
       
        for player in [first_player, second_player]:
            player_power = self.power_per_player[player]
            if player_power >= 3 and game_utilities.has_presence(game_state["tiles"][index_of_tile_burned_at], player):
                points_gained = 3 if player_power >= 5 else 2
                game_state["points"][player] += points_gained
                await send_clients_log_message(f"{player} gains {points_gained} points from {self.name} due to a shape being burned on {game_state['tiles'][index_of_tile_burned_at].name}")