import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SigilOfJustice(Tile):
    def __init__(self):
        super().__init__(
            name="Sigil of Justice",
            type="Scorer",
            number_of_slots=3,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "When one of your disciples is ++exiled++, +3 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_cooldown": False,
                },
            ],
        )
 
    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_exile"][self.name] = self.on_exile_effect

    async def on_exile_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        index_of_tile_exiled_from = data.get('index_of_tile_exiled_from')
        tile_exiled_from = game_state['tiles'][index_of_tile_exiled_from]
        exiler = data.get('exiler')
        exiled_disciple = data.get('disciple')
        
        self.determine_influence()        
        ruler = self.determine_ruler(game_state)
        player_influence = self.influence_per_player[exiler]

        if player_influence >= self.influence_tiers[0]['influence_to_reach_tier'] and exiled_disciple['color'] == ruler:
            points_gained = 3
            game_state["points"][ruler] += points_gained
            await send_clients_log_message(f"{exiler} gains {points_gained} points from **{self.name}** due to their {exiled_disciple['color']}_{exiled_disciple['disciple']} being exiled from **{tile_exiled_from.name}**")