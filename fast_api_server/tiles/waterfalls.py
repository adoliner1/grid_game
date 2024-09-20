import game_utilities
import game_constants
from tiles.tile import Tile

class Waterfalls(Tile):
    def __init__(self):
        super().__init__(
            name="Waterfalls",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": False,
                    "description": "At the __end of a round__, +1 points per tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,    
                    "leader_must_be_present": False,                 
                },
                {
                    "influence_to_reach_tier": 7,
                    "must_be_ruler": True,
                    "description": "At the __end of a round__, +2 points per tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,         
                    "leader_must_be_present": False,            
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            player_influence = self.influence_per_player[player]
            if player_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
                tiles_present_at = sum(1 for tile in game_state["tiles"] if game_utilities.has_presence(tile, player))
                points_per_tile = 2 if player_influence >= self.influence_tiers[1]['influence_to_reach_tier'] else 1
                points_awarded = tiles_present_at * points_per_tile
                game_state["points"][player] += points_awarded
                await send_clients_log_message(f"{player} gains {points_awarded} points from {self.name} for being present at {tiles_present_at} tiles with {player_influence} influence")