import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class DarkPortal(Tile):
    def __init__(self):
        super().__init__(
            name="Dark Portal",
            type="Leader-Movement/Burner",
            minimum_influence_to_rule=2,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": False,
                    "description": "**Action:** If you have an acolyte here, ^^burn^^ one of your disciples anywhere then teleport anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": ['disciple_to_burn', 'tile_to_teleport_to'],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)
    
    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action

        if current_piece_of_data_to_fill == "disciple_to_burn":
            slots_with_a_user_disciple = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_user_disciples_on_this_tile = []
                for slot_index, slot in enumerate(tile.slots_for_disciples):
                    if slot and slot['color'] == user:
                        slots_with_user_disciples_on_this_tile.append(slot_index)
                if slots_with_user_disciples_on_this_tile:
                    slots_with_a_user_disciple[index] = slots_with_user_disciples_on_this_tile
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_user_disciple
        else:
            available_actions["select_a_tile"] = game_constants.all_tile_indices

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        
        acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == whose_turn_is_it and slot["disciple"] == "acolyte")
       
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]["is_on_cooldown"] and
            whose_turn_is_it == ruler and
            acolyte_count > 0):
                useable_tiers.append(0)
       
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_per_player[user] < self.influence_tiers[0]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False
        
        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False

        # Check if the user has an acolyte on this tile
        acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == user and slot["disciple"] == "acolyte")
        if acolyte_count == 0:
            await send_clients_log_message(f"You need an acolyte on **{self.name}** to use its action")
            return False

        index_of_tile_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']
        slot_index_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_tile_to_move_leader_to = game_action_container.required_data_for_action['tile_to_teleport_to']
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn from {game_state['tiles'][index_of_tile_to_burn_disciple_from].name}")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from]['color'] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple that doesn't belong to them")
            return False

        tile_to_move_leader_to = game_state['tiles'][index_of_tile_to_move_leader_to]
        if index_of_tile_to_move_leader_to is None or index_of_tile_to_move_leader_to > 8:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False

        # Burn the disciple
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_from, slot_index_to_burn_disciple_from)
        await send_clients_log_message(f"{user} burned a disciple on {game_state['tiles'][index_of_tile_to_burn_disciple_from].name}")

        # Move the leader
        await send_clients_log_message(f"{user}_leader took **{self.name}** to **{tile_to_move_leader_to.name}**")
        tile_index_of_leader = game_utilities.get_tile_index_of_leader(game_state, user)
        game_state['tiles'][tile_index_of_leader].leaders_here[user] = False
        tile_to_move_leader_to.leaders_here[user] = True

        self.influence_tiers[0]["is_on_cooldown"] = True
        return True
