import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class StaffOfTheMoon(Tile):
    def __init__(self):
        super().__init__(
            name="Staff of the Moon",
            type="Tile-Mover",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** Swap any tile with a tile adjacent to it",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "leader_must_be_present": True,
                    "data_needed_for_use": ["tile_to_swap", "other_tile_to_swap"]
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
            whose_turn_is_it == ruler and
            self.leaders_here[whose_turn_is_it]):
                useable_tiers.append(0)
       
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill == "tile_to_swap":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill == "other_tile_to_swap":
            tile1_index = game_action_container.required_data_for_action["tile_to_swap"]
            available_tiles = [i for i in range(len(game_state["tiles"])) 
                               if i != tile1_index and game_utilities.determine_if_directly_adjacent(tile1_index, i)]
            available_actions["select_a_tile"] = available_tiles

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

        if not self.leaders_here[user]:
            await send_clients_log_message(f"Your leader must be present to use **{self.name}**")
            return False

        tile1_index = game_action_container.required_data_for_action["tile_to_swap"]
        tile2_index = game_action_container.required_data_for_action["other_tile_to_swap"]
       
        if tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid tiles selected for using **{self.name}**")
            return False
       
        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for **{self.name}**")
            return False

        if not game_utilities.determine_if_directly_adjacent(tile1_index, tile2_index):
            await send_clients_log_message(f"Selected tiles must be adjacent for **{self.name}**")
            return False

        await send_clients_log_message(f"{user} used **{self.name}** to swap **{game_state['tiles'][tile1_index].name}** and **{game_state['tiles'][tile2_index].name}**")
        
        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]
       
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True