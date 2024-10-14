import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SigilOfAsh(Tile):
    def __init__(self):
        super().__init__(
            name="Sigil of Ash",
            type="Scorer",
            number_of_slots=3,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "When you ^^burn^^, +2 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_cooldown": False,
                },
            ],
        )
 
    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        burner = data.get('burner')
        self.determine_influence()        

        if self.influence_per_player[burner] >= self.influence_tiers[0]["influence_to_reach_tier"]:
            points_gained = 2
            game_state["points"][burner] += points_gained
            await send_clients_log_message(f"{burner} burned and gains {points_gained} points from **{self.name}**.")