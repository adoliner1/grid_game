import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class StaffOfCommand(Tile):
    def __init__(self):
        super().__init__(
            name="Staff of Command",
            type="Disciple-Mover",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** Move one of your disciples anywhere to a tile adjacent to it",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": True,
                    "data_needed_for_use": ["disciple_to_move", "slot_to_move_disciple_to"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        player_influence = self.influence_per_player[whose_turn_is_it]

        if (player_influence >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            self.determine_ruler(game_state) == whose_turn_is_it and
            not self.influence_tiers[0]["is_on_cooldown"] and
            self.leaders_here[whose_turn_is_it]):
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action

        if current_piece_of_data_to_fill == "disciple_to_move":
            slots_with_user_disciples = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_user_disciples_on_this_tile = [
                    i for i, slot in enumerate(tile.slots_for_disciples)
                    if slot and slot["color"] == user
                ]
                if slots_with_user_disciples_on_this_tile:
                    slots_with_user_disciples[index] = slots_with_user_disciples_on_this_tile
            available_actions["select_a_slot_on_a_tile"] = slots_with_user_disciples

        elif current_piece_of_data_to_fill == "slot_to_move_disciple_to":
            tile_index_from = game_action_container.required_data_for_action['disciple_to_move']['tile_index']
            adjacent_tiles = game_utilities.get_adjacent_tile_indices(tile_index_from)
            slots_without_a_disciple_per_tile = {}
            for tile_index in adjacent_tiles:
                tile = game_state["tiles"][tile_index]
                slots_without_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if not slot]
                if slots_without_disciples:
                    slots_without_a_disciple_per_tile[tile_index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple_per_tile

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_influence = self.influence_per_player[user]

        if user_influence < self.influence_tiers[tier_index]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False

        if self.determine_ruler(game_state) != user:
            await send_clients_log_message(f"You must be the ruler to use **{self.name}**")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        if not self.leaders_here[user]:
            await send_clients_log_message(f"Your leader must be present on **{self.name}** to use it")
            return False

        tile_index_from = game_action_container.required_data_for_action['disciple_to_move']['tile_index']
        slot_index_from = game_action_container.required_data_for_action['disciple_to_move']['slot_index']
        slot_index_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['tile_index']

        source_tile = game_state["tiles"][tile_index_from]
        if source_tile.slots_for_disciples[slot_index_from] is None or source_tile.slots_for_disciples[slot_index_from]["color"] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose an invalid disciple to move")
            return False

        if game_state["tiles"][tile_index_to].slots_for_disciples[slot_index_to] is not None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot that is not empty to move to")
            return False

        if not game_utilities.determine_if_directly_adjacent(tile_index_from, tile_index_to):
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a non-adjacent tile to move to")
            return False

        await send_clients_log_message(f"Using **{self.name}**")
        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        
        return True