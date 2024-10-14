import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class PrincesssAdmirers(Tile):
    def __init__(self):
        super().__init__(
            name="Princess's Admirers",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "At the __end of each round__, gain points equal to your presence",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,    
                    "leader_must_be_present": False,                
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_expected_incomes(self, game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            ruler_influence = self.influence_per_player[ruler]
            if ruler_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
                tiles_present_at = sum(1 for tile in game_state["tiles"] if game_utilities.has_presence(tile, ruler))
                points_awarded = tiles_present_at
                game_state["expected_points_incomes"][ruler] += points_awarded

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            ruler_influence = self.influence_per_player[ruler]
            if ruler_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
                tiles_present_at = sum(1 for tile in game_state["tiles"] if game_utilities.has_presence(tile, ruler))
                points_awarded = tiles_present_at
                game_state["points"][ruler] += points_awarded
                await send_clients_log_message(f"{ruler} gains {points_awarded} points from **{self.name}** for being present at {tiles_present_at} tiles")