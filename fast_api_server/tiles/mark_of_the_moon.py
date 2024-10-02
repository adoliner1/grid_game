import game_utilities
import game_constants
from tiles.tile import Tile

class MarkOfTheMoon(Tile):
    def __init__(self):
        super().__init__(
            name="Mark of the Moon",
            type="Tile-Mover",
            minimum_influence_to_rule=2,
            number_of_slots=2,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": True,
                    "description": "**Action:** Swap Mark of the Moon with a tile adjacent to it",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "leader_must_be_present": False,
                    "data_needed_for_use": ["tile_to_swap_with"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
       
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]["is_on_cooldown"] and
            whose_turn_is_it == ruler):
                useable_tiers.append(0)
       
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        mark_of_moon_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        adjacent_tiles = game_utilities.get_adjacent_tile_indices(mark_of_moon_index)
        available_actions["select_a_tile"] = adjacent_tiles

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

        tile_to_swap_with = game_action_container.required_data_for_action["tile_to_swap_with"]
        mark_of_moon_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
       
        if tile_to_swap_with is None:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False
       
        if not game_utilities.determine_if_directly_adjacent(mark_of_moon_index, tile_to_swap_with):
            await send_clients_log_message(f"Can only swap with adjacent tiles using **{self.name}**")
            return False

        await send_clients_log_message(f"Used **{self.name}** to swap with **{game_state['tiles'][tile_to_swap_with].name}**")
        
        # Swap the tiles
        game_state["tiles"][mark_of_moon_index], game_state["tiles"][tile_to_swap_with] = game_state["tiles"][tile_to_swap_with], game_state["tiles"][mark_of_moon_index]
       
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True