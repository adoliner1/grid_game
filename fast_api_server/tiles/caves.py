import game_utilities
import game_constants
from tiles.tile import Tile

class Caves(Tile):
    def __init__(self):
        super().__init__(
            name="Caves",
            type="Giver",
            number_of_slots=5,
            minimum_influence_to_rule=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "After you ((recruit)) at an adjacent tile, if you have less than 5 influence there, [[receive]] a follower there",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                    
                },
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": False,                    
                    "description": "Same as above but less than 7 influence",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_a_cooldown": False,                    
                },
                {
                    "influence_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "Same as above but less than 9 influence",
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
        index_of_tile_recruited_at = data.get('index_of_tile_recruited_at')
        tile_recruited_at = game_state['tiles'][index_of_tile_recruited_at]
        recruiter_influence_at_tile_recruited_at = tile_recruited_at.influence_per_player[recruiter]
        self.determine_influence()
        ruler = self.determine_ruler(game_state)
        recruiter_influence_here = self.influence_per_player[recruiter]
        index_of_caves = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        is_adjacent = game_utilities.determine_if_directly_adjacent(index_of_caves, index_of_tile_recruited_at)

        if not is_adjacent:
            return      

        recruiter_receives_follower = False

        if recruiter_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and recruiter_influence_at_tile_recruited_at <= 5:
            recruiter_receives_follower = True
        elif recruiter_influence_here >= self.influence_tiers[1]['influence_to_reach_tier'] and recruiter_influence_at_tile_recruited_at <= 7:
            recruiter_receives_follower = True
        elif recruiter_influence_here >= self.influence_tiers[2]['influence_to_reach_tier'] and recruiter == ruler and recruiter_influence_at_tile_recruited_at <= 9:
            recruiter_receives_follower = True
    
        if recruiter_receives_follower:
            await game_utilities.player_receives_a_disciple_on_tile(
                game_state, game_action_container_stack, send_clients_log_message,
                get_and_send_available_actions, send_clients_game_state,
                recruiter, tile_recruited_at, 'follower'
            )
        
        await send_clients_log_message(f"{recruiter} receives a {recruiter}_follower at {tile_recruited_at.name} from **{self.name}**")