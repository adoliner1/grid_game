import game_utilities
import game_constants
from tiles.tile import Tile

class Pluto(Tile):
    def __init__(self):
        super().__init__(
            name="Pluto",
            type="Power-Creator",
            minimum_influence_to_rule=3,
            number_of_slots=7,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 6,
                    "must_be_ruler": False,
                    "description": "**Action:** ^^Burn^^ a follower here for +3 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": False,
                    "data_needed_for_use": []
                },
                {
                    "influence_to_reach_tier": 8,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ 2 followers for +8 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False,
                    "data_needed_for_use": [],
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        user = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        
        followers = [slot for slot in self.slots_for_disciples if slot and slot["disciple"] == "follower" and slot["color"] == user]

        if (not self.influence_tiers[0]['is_on_cooldown'] and 
            self.influence_per_player[user] >= self.influence_tiers[0]['influence_to_reach_tier'] and 
            len(followers) >= 1):
            useable_tiers.append(0)
        if (not self.influence_tiers[1]['is_on_cooldown'] and 
            self.influence_per_player[user] >= self.influence_tiers[1]['influence_to_reach_tier'] and 
            user == ruler and
            len(followers) >= 2):
            useable_tiers.append(1)

        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"{self.name} tier {tier_index} is on cooldown")
            return False

        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on {self.name} to use tier {tier_index}")
            return False

        if tier_index == 1 and user != ruler:
            await send_clients_log_message(f"You must be the ruler to use {tier_index} of {self.name}")
            return False

        index_of_pluto = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        followers_to_burn = [i for i, slot in enumerate(self.slots_for_disciples)
                           if slot and slot["disciple"] == "follower" and slot["color"] == user]

        followers_required = 1 if tier_index == 0 else 2
        if len(followers_to_burn) < followers_required:
            await send_clients_log_message(f"Not enough followers to burn on {self.name}")
            return False

        await send_clients_log_message(f"Using {self.name} tier {tier_index}")

        for i in followers_to_burn[:followers_required]:
            await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_pluto, i)

        power_gained = 3 if tier_index == 0 else 8
        game_state['power'][user] += power_gained
        await send_clients_log_message(f"{user} gains {power_gained} power from {self.name}")

        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True