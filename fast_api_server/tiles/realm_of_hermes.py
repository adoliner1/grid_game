import asyncio
import game_action_container
from tile import Tile
import game_utilities
import game_constants

class RealmOfHermes(Tile):
    def __init__(self):
        super().__init__(
            name="Realm of Hermes",
            type="Leader-Movement",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "**Action:** If you have at least 1 disciple here, ^^burn^^ all your disciples here. If you burned at least 4 influence worth, increase your leader movement by 1",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "leader_must_be_present": False,
                    "data_needed_for_use": []
                },
            ],
            TILE_PRIORITY=-1
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        if ruler == whose_turn_is_it and not self.influence_tiers[0]["is_on_cooldown"] and game_utilities.count_all_disciples_for_color_on_tile(whose_turn_is_it, self) > 0:
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if ruler != user:
            await send_clients_log_message(f"{user} is not the ruler of **{self.name}** and cannot use it")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of **{self.name}** is on cooldown")
            return False

        if not game_utilities.has_presence(self, user):
            await send_clients_log_message(f"Don't have a disciple on **{self.name}**")
            return False

        realm_of_hermes_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        influence_burned = 0
        disciples_burned = 0

        for i, slot in enumerate(self.slots_for_disciples):
            if slot and slot["color"] == ruler:
                disciple_type = slot["disciple"]
                influence_burned += game_constants.disciple_influence[disciple_type]
                await game_utilities.burn_disciple_at_tile_at_index(
                    game_state, game_action_container_stack, send_clients_log_message,
                    get_and_send_available_actions, send_clients_game_state,
                    realm_of_hermes_index, i
                )
                disciples_burned += 1

        await send_clients_log_message(f"{ruler} burned {disciples_burned} disciples (worth {influence_burned} influence) on **{self.name}**")

        if influence_burned >= 4:
            game_state['leader_movement'][ruler] += 1
            await send_clients_log_message(f"{ruler}'s leader movement increased by 1 from **{self.name}**")

        return True