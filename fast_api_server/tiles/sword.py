import game_utilities
import game_constants
from tiles.tile import Tile

class Sword(Tile):
    def __init__(self):
        super().__init__(
            name="Sword",
            type="Attacker",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** Pay one power to ^^burn^^ any disciple at an adjacent tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": ["slot_and_tile_to_burn_disciple_at"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if (ruler == whose_turn_is_it and not self.influence_tiers[0]["is_on_cooldown"] and game_state['power'][whose_turn_is_it] > 0):
            useable_tiers.append(0)
        
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        slots_with_a_burnable_disciple = {}
        indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["index_of_tile_in_use"])
        for index in indices_of_adjacent_tiles:
            slots_with_disciples = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_disciples) if slot]
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

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if game_state['power'][user] < 1:
            await send_clients_log_message(f"Not enough power to use **{self.name}**")
            return False

        index_of_sword = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_disciple_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_disciple_at']['slot_index']
        index_of_tile_to_burn_disciple_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_disciple_at']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_sword, index_of_tile_to_burn_disciple_at):
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a non-adjacent tile")
            return False
        
        if game_state["tiles"][index_of_tile_to_burn_disciple_at].slots_for_disciples[slot_index_to_burn_disciple_at] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to burn at {game_state['tiles'][index_of_tile_to_burn_disciple_at].name}")
            return False
        
        await send_clients_log_message(f"{user} uses **{self.name}** and loses one power")
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple_at, slot_index_to_burn_disciple_at)

        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True