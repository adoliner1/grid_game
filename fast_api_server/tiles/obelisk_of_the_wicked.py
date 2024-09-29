import game_utilities
import game_constants
from tiles.tile import Tile

class ObeliskOfTheWicked(Tile):
    def __init__(self):
        super().__init__(
            name="Obelisk of the Wicked",
            type="Giver/Exile-Enhancer",
            number_of_slots=3,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "After you exile, if you have less than 4 influence at the tile the disciple was exiled from, [[receive]] a follower there",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_a_cooldown": False,                    
                },                            
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_exile"][self.name] = self.on_exile_effect

    async def on_exile_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        exiler = data.get('exiler')
        ruler = self.determine_ruler()
        index_of_tile_exiled_from = data.get('index_of_tile_exiled_from')
        tile_exiled_from = game_state['tiles'][index_of_tile_exiled_from]
        exiler_influence_at_tile_exiled_from = tile_exiled_from.influence_per_player[exiler]
        
        self.determine_influence()
        exiler_influence_here = self.influence_per_player[exiler]

        exiler_receives_follower = False
        if exiler_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and exiler_influence_at_tile_exiled_from < 4 and ruler == exiler:
            exiler_receives_follower = True
   
        if exiler_receives_follower:
            await game_utilities.player_receives_a_disciple_on_tile(
                game_state, game_action_container_stack, send_clients_log_message,
                get_and_send_available_actions, send_clients_game_state,
                exiler, tile_exiled_from, 'follower'
            )
       
            await send_clients_log_message(f"{exiler} receives a {exiler}_follower at **{tile_exiled_from.name}** from **{self.name}**")