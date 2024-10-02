import game_utilities
import game_constants
from tiles.tile import Tile

class Orbit(Tile):
    def __init__(self):
        super().__init__(
            name="Orbit",
            type="Tile-Mover",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** Choose a tile. Rotate the row that tile is in left once (the leftmost tile becomes the rightmost).",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,    
                    "leader_must_be_present": False,                  
                    "data_needed_for_use": ["tile_in_the_row_you_want_to_rotate"]
                },
            ]      
        )

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        if not self.influence_tiers[0]["is_on_cooldown"] and self.determine_ruler(game_state) == whose_turn_is_it:
            useable_tiers.append(0)

        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["select_a_tile"] = game_constants.all_tile_indices

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

        tile_in_the_row_you_want_to_rotate = game_action_container.required_data_for_action['tile_in_the_row_you_want_to_rotate']
        if tile_in_the_row_you_want_to_rotate is None:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False

        # Determine the row from the tile index
        row_to_shift = tile_in_the_row_you_want_to_rotate // 3
        # Shift the row of tiles
        row_start_index = row_to_shift * 3
        row_end_index = row_start_index + 3
        row_tiles = game_state["tiles"][row_start_index:row_end_index]
        # Perform the shift
        shifted_row_tiles = row_tiles[1:] + row_tiles[:1]
        tile_names = [tile.name for tile in row_tiles]
        await send_clients_log_message(f"Using **{self.name}** to rotate the row containing tiles ({', '.join(tile_names)})")
        # Update the game state with the shifted row
        game_state["tiles"][row_start_index:row_end_index] = shifted_row_tiles
        
        self.influence_tiers[0]['is_on_cooldown'] = True
        return True