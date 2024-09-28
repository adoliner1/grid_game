import game_utilities
import game_constants
from tiles.tile import Tile

class QueensRetinue(Tile):
    def __init__(self):
        super().__init__(
            name="Queen's Retinue",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "When your opponent ((recruits)) a disciple on an adjacent tile, +2 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                    
                },
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,                    
                    "description": "When your opponent ((recruits)) a disciple on an adjacent tile, +3 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                    
                },
            ]            
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_recruit"][self.name] = self.on_recruit_effect

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        recruiter = data.get('recruiter')
        tile_index = data.get('index_of_tile_recruited_at')
        queen_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if not game_utilities.determine_if_directly_adjacent(tile_index, queen_index):
            return

        other_player = 'red' if recruiter == 'blue' else 'blue'
        ruler = self.determine_ruler(game_state)
        other_player_influence = self.influence_per_player[other_player]

        points_earned = 0
        if other_player_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
            points_earned += 2
        if ruler == other_player and self.influence_tiers[1]['influence_to_reach_tier']:
            points_earned += 3

        if points_earned > 0:
            game_state["points"][other_player] += points_earned
            await send_clients_log_message(f"{other_player} earned {points_earned} points from **{self.name}**")