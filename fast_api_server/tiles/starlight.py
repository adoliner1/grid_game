import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class Starlight(Tile):
    def __init__(self):
        super().__init__(
            name="Starlight",
            type="Tile-Mover",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** Swap a tile in Starlight's row with a tile in its column",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,    
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": ["tile_that_shares_a_row_with_starlight", "tile_that_shares_a_column_with_starlight"],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
       
        if not self.influence_tiers[0]["is_on_cooldown"] and self.determine_ruler(game_state) == whose_turn_is_it:
            useable_tiers.append(0)
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        starlight_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        starlight_row = starlight_index // 3
        starlight_column = starlight_index % 3

        if current_piece_of_data_to_fill == "tile_that_shares_a_row_with_starlight":
            available_actions["select_a_tile"] = [i for i in range(starlight_row * 3, (starlight_row + 1) * 3)]
        elif current_piece_of_data_to_fill == "tile_that_shares_a_column_with_starlight":
            available_actions["select_a_tile"] = [i for i in range(starlight_column, 9, 3)]

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
       
        if not ruler:
            await send_clients_log_message(f"No ruler determined for **{self.name}**, cannot use")
            return False
       
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use **{self.name}**")
            return False
       
        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        tile_in_row = game_action_container.required_data_for_action['tile_that_shares_a_row_with_starlight']
        tile_in_column = game_action_container.required_data_for_action['tile_that_shares_a_column_with_starlight']

        if tile_in_row is None or tile_in_column is None:
            await send_clients_log_message(f"Invalid tiles selected for using **{self.name}**")
            return False

        # Swap the tiles
        game_state["tiles"][tile_in_row], game_state["tiles"][tile_in_column] = game_state["tiles"][tile_in_column], game_state["tiles"][tile_in_row]

        await send_clients_log_message(f"Using **{self.name}** to swap {game_state['tiles'][tile_in_row].name} with {game_state['tiles'][tile_in_column].name}")

        self.influence_tiers[0]['is_on_cooldown'] = True
        return True