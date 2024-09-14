import game_utilities
import game_constants
from tiles.tile import Tile

class Waterfalls(Tile):
    def __init__(self):
        super().__init__(
            name="Waterfalls",
            type="Scorer",
            minimum_power_to_rule=2,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "At the __end of a round__, +1 point per tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "At the __end of a round__, +2 points per tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            player_power = self.power_per_player[player]
            if player_power >= self.power_tiers[0]['power_to_reach_tier']:
                tiles_present_at = sum(1 for tile in game_state["tiles"] if game_utilities.has_presence(tile, player))
                points_per_tile = 2 if player_power >= self.power_tiers[1]['power_to_reach_tier'] else 1
                points_awarded = tiles_present_at * points_per_tile
                game_state["points"][player] += points_awarded
                await send_clients_log_message(f"{player} gains {points_awarded} points from {self.name} for being present at {tiles_present_at} tiles with {player_power} power")