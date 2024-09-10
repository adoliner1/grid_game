import game_utilities
import game_constants
from tiles.tile import Tile

class Wormhole(Tile):
    def __init__(self):
        super().__init__(
            name="Wormhole",
            type="Tile-Mover",
            minimum_power_to_rule=3,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "**Action:** If you have at least two different shapes here, once per round, swap the position of two tiles",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                     
                    "data_needed_for_use": ["tile1", "tile2"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        if (self.power_per_player[whose_turn_is_it] >= self.power_tiers[0]['power_to_reach_tier'] and 
            not self.power_tiers[0]["is_on_cooldown"]):
            shapes = set(slot["shape"] for slot in self.slots_for_shapes if slot and slot["color"] == whose_turn_is_it)
            if len(shapes) >= 2:
                useable_tiers.append(0)
        
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill == "tile1":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill == "tile2":
            available_tiles = list(range(len(game_state["tiles"])))
            tile1_index = game_action_container.required_data_for_action["tile1"]
            if tile1_index is not None:
                available_tiles.remove(tile1_index)
            available_actions["select_a_tile"] = available_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action

        if self.power_per_player[user] < self.power_tiers[0]['power_to_reach_tier']:
            await send_clients_log_message(f"Not enough power to use {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"{self.name} is on cooldown")
            return False

        shapes = set(slot["shape"] for slot in self.slots_for_shapes if slot and slot["color"] == user)
        if len(shapes) < 2:
            await send_clients_log_message(f"Player does not have at least 2 different shapes on {self.name}")
            return False

        tile1_index = game_action_container.required_data_for_action['tile1']
        tile2_index = game_action_container.required_data_for_action['tile2']
        
        if tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid tiles selected for using {self.name}")
            return False
        
        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for {self.name}")
            return False

        await send_clients_log_message(f"Used {self.name} to swap {game_state['tiles'][tile1_index].name} and {game_state['tiles'][tile2_index].name}")
        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]
        
        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True