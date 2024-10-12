import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class AltarOfHades(Tile):
    def __init__(self):
        super().__init__(
            name="Altar of Hades",
            type="Generator/Burner",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** ^^Burn^^ one of your disciples on another tile for +5 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": True,                  
                    "data_needed_for_use": ['disciple_to_burn'],
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)
    
    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        user = game_action_container.whose_action
        slots_with_a_user_disciple = {}
        for index, tile in enumerate(game_state["tiles"]):
            if tile.name != self.name:
                slots_with_user_disciples_on_this_tile = []
                for slot_index, slot in enumerate(tile.slots_for_disciples):
                    if slot and slot['color'] == user:
                        slots_with_user_disciples_on_this_tile.append(slot_index)
                if slots_with_user_disciples_on_this_tile:
                    slots_with_a_user_disciple[index] = slots_with_user_disciples_on_this_tile
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_user_disciple

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
       
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]["is_on_cooldown"] and
            whose_turn_is_it == ruler and self.leaders_here[ruler]):
                useable_tiers.append(0)
       
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        index_of_tile_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']
        slot_index_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
       
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** tier {tier_index} is on cooldown")
            return False
        
        if self.leaders_here[user] == False:
            await send_clients_log_message(f"Tried to use **{self.name}** but {user}_leader isn't present")
            return False            
       
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use tier {tier_index}")
            return False
       
        if tier_index == 1 and self.determine_ruler(game_state) != user:
            await send_clients_log_message(f"You must be the ruler to use **{self.name}**")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn from {game_state['tiles'][index_of_tile_to_burn_disciple_from].name}")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from]['color'] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple that doesn't belong to them")
            return False
        
        if index_of_tile_to_burn_disciple_from == game_utilities.find_index_of_tile_by_name(game_state, self.name):
            await send_clients_log_message(f"Cannot burn from **{self.name}**")
            return False            

        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_from, slot_index_to_burn_disciple_from)
        
        power_gained = 5
        game_state['power'][user] += power_gained
        await send_clients_log_message(f"{user} gains {power_gained} power from **{self.name}**")
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True