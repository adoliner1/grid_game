import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class EternalLattice(Tile):
    def __init__(self):
        super().__init__(
            name="Eternal Lattice",
            type="Generator",
            minimum_influence_to_rule=3,
            description="",
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "**Action:** Gain 1 power for each tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": True,
                    "data_needed_for_use": [],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if (ruler == whose_turn_is_it and 
            self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]['is_on_cooldown'] and
            self.leaders_here[ruler]):
            useable_tiers.append(0)
        
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False

        if self.influence_per_player[user] < self.influence_tiers[0]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False

        if not self.leaders_here[user]:
            await send_clients_log_message(f"Leader must be present to use **{self.name}**")
            return False

        tiles_present_at = sum(1 for tile in game_state["tiles"] if game_utilities.has_presence(tile, user))
        power_gained = tiles_present_at

        game_state['power'][user] += power_gained
        await send_clients_log_message(f"{user} gains {power_gained} power from **{self.name}** for being present at {tiles_present_at} tiles")

        self.influence_tiers[0]['is_on_cooldown'] = True
        return True