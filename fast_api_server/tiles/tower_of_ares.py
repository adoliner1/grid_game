import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class TowerOfAres(Tile):
    def __init__(self):
        super().__init__(
            name="Tower of Ares",
            type="Attacker",
            minimum_influence_to_rule=4,
            number_of_slots=4,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ one of your disciples here, then ^^burn^^ a disciple at a tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": False,                
                    "data_needed_for_use": ["disciple_to_burn_on_tower_of_ares", "disciple_to_burn"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        player_influence = self.influence_per_player[whose_turn_is_it]
        ruler = self.determine_ruler(game_state)

        if (player_influence >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            not self.influence_tiers[0]["is_on_cooldown"] and 
            whose_turn_is_it == ruler) and game_utilities.has_presence(self, whose_turn_is_it):
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action

        if current_piece_of_data_to_fill == "disciple_to_burn_on_tower_of_ares":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_disciple_of_player_color_at_tile_index(game_state, user, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill == "disciple_to_burn":
            slots_with_a_burnable_disciple = {}
            for index, tile in enumerate(game_state["tiles"]):
                if game_utilities.has_presence(tile, user):
                    slots_with_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if slot]
                    if slots_with_disciples:
                        slots_with_a_burnable_disciple[index] = slots_with_disciples
            
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_disciple

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_influence = self.influence_per_player[user]
        ruler = self.determine_ruler(game_state)

        if user_influence < self.influence_tiers[tier_index]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use tier {tier_index} of **{self.name}**")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of **{self.name}** is on cooldown")
            return False

        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use tier {tier_index} of **{self.name}**")
            return False

        index_of_spear = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_disciple_from_here = game_action_container.required_data_for_action['disciple_to_burn_on_tower_of_ares']['slot_index']
        slot_index_to_burn_disciple_at = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_tile_to_burn_disciple_at = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']

        if not game_utilities.has_presence(game_state["tiles"][index_of_tile_to_burn_disciple_at], user):
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a tile where they're not present")
            return False

        if self.slots_for_disciples[slot_index_to_burn_disciple_from_here] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn at **{self.name}**")
            return False

        if game_state["tiles"][index_of_tile_to_burn_disciple_at].slots_for_disciples[slot_index_to_burn_disciple_at] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn at {game_state['tiles'][index_of_tile_to_burn_disciple_at].name}")
            return False

        if self.slots_for_disciples[slot_index_to_burn_disciple_from_here]["color"] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple that didn't belong to them")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of **{self.name}**")
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_spear, slot_index_to_burn_disciple_from_here)
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_at, slot_index_to_burn_disciple_at)

        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True