import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class PrincesEntourage(Tile):
    def __init__(self):
        super().__init__(
            name="Prince's Entourage",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=6,
            description="",
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "After you ++exile++, gain points equal to the number of disciples you have on Prince's Entourage",
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
        ruler = self.determine_ruler(game_state)
        exiler_influence = self.influence_per_player[exiler]

        if exiler == ruler and exiler_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
            disciples_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == exiler)
            points_gained = disciples_count

            if points_gained > 0:
                game_state["points"][exiler] += points_gained
                await send_clients_log_message(f"{exiler} gained {points_gained} points from **{self.name}** for exiling with {disciples_count} disciples present")
