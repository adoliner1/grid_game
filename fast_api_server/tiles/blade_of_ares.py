import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class BladeOfAres(Tile):
    def __init__(self):
        super().__init__(
            name="Blade of Ares",
            type="Burner",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ any disciple at a tile you rule",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": True,                  
                    "data_needed_for_use": ["disciple_to_burn"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if (ruler == whose_turn_is_it and not self.influence_tiers[0]["is_on_cooldown"] and self.leaders_here[ruler]):
            useable_tiers.append(0)
        
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        slots_with_a_burnable_disciple = {}
        for index, tile in enumerate(game_state["tiles"]):
            if tile.determine_ruler(game_state) == game_state["whose_turn_is_it"]:
                slots_with_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if slot]
                if slots_with_disciples:
                    slots_with_a_burnable_disciple[index] = slots_with_disciples
        available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_disciple

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

        slot_index_to_burn_disciple_at = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_tile_to_burn_disciple_at = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']

        if game_state["tiles"][index_of_tile_to_burn_disciple_at].determine_ruler(game_state) != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a tile you don't rule")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_at].slots_for_disciples[slot_index_to_burn_disciple_at] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn at {game_state['tiles'][index_of_tile_to_burn_disciple_at].name}")
            return False
        
        await send_clients_log_message(f"{user} uses **{self.name}**")
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_at, slot_index_to_burn_disciple_at)

        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True