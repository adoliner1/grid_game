import asyncio
import game_action_container
from .tile import Tile
from statuses.status import Status
import game_utilities
import game_constants

class ZealotsEnclaveStatus(Status):
    def __init__(self, duration, player_with_status):
        super().__init__(
            name="Zealots Enclave",
            description="Recruitment range is increased by 1 (Zealot's Enclave)",
            duration=duration,
            player_with_status=player_with_status
        )

    def modify_recruiting_ranges(self, game_state):
        game_state['recruiting_range'][self.player_with_status] += 1

class ZealotsEnclave(Tile):
    def __init__(self):
        super().__init__(
            name="Zealot's Enclave",
            type="Recruitment-Enhancer",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "Increase your ((recruitment)) range by 1 for the rest of the round",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "leader_must_be_present": True,
                    "data_needed_for_use": []
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
            not self.influence_tiers[0]["is_on_cooldown"] and 
            self.leaders_here[ruler] and
            self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']):
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False
        if not self.leaders_here[ruler]:
            await send_clients_log_message(f"Leader must be at **{self.name}** to use it")
            return False                  
        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        await send_clients_log_message(f"{user} uses **{self.name}**")
        self.influence_tiers[tier_index]["is_on_cooldown"] = True

        zealots_status = ZealotsEnclaveStatus(duration="round", player_with_status=user)
        game_state["statuses"].append(zealots_status)

        return True