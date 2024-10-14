import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class RealmOfHermes(Tile):
    def __init__(self):
        super().__init__(
            name="Realm of Hermes",
            type="Leader-Movement/Burner",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ one of your disciples anywhere. Gain leader_movement equal to the influence burned",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": True,
                    "data_needed_for_use": ['disciple_to_burn'],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        user = game_action_container.whose_action
        slots_with_a_user_disciple = {}
        for index, tile in enumerate(game_state["tiles"]):
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
        if (ruler == whose_turn_is_it and 
            not self.influence_tiers[0]["is_on_cooldown"] and 
            self.leaders_here[whose_turn_is_it] and
            any(game_utilities.has_presence(tile, whose_turn_is_it) for tile in game_state["tiles"])):
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
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if self.leaders_here[user] == False:
            await send_clients_log_message(f"Tried to use **{self.name}** but {user}_leader isn't present")
            return False  

        index_of_tile_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']
        slot_index_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']

        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn from {game_state['tiles'][index_of_tile_to_burn_disciple_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from]['color'] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple that doesn't belong to them")
            return False

        # Burn the disciple and calculate influence
        disciple_type = game_state["tiles"][index_of_tile_to_burn_disciple_from].slots_for_disciples[slot_index_to_burn_disciple_from]['disciple']
        influence_burned = game_constants.disciple_influence[disciple_type]
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_from, slot_index_to_burn_disciple_from)
        
        # Increase leader movement
        game_state['leader_movement'][user] += influence_burned

        await send_clients_log_message(f"{user} gains {influence_burned} leader_movement from **{self.name}**")

        self.influence_tiers[0]["is_on_cooldown"] = True
        return True