import game_utilities
import game_constants
from tiles.tile import Tile

class RedDwarf(Tile):
    def __init__(self):
        super().__init__(
            name="Red Dwarf",
            type="Tile-Mover",
            minimum_influence_to_rule=2,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 1,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your disciples here to swap the position of 2 tiles",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,            
                    "leader_must_be_present": False,         
                    "data_needed_for_use": ["slot_to_burn_from_on_red_dwarf", "first_tile", "second_tile"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        if self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and any(slot for slot in self.slots_for_disciples if slot and slot["color"] == whose_turn_is_it):
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        
        if current_piece_of_data_to_fill == "slot_to_burn_from_on_red_dwarf":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_disciple_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill == "first_tile":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill == "second_tile":
            first_tile = game_action_container.required_data_for_action.get("first_tile")
            available_tiles = list(range(len(game_state["tiles"])))
            if first_tile is not None:
                available_tiles.remove(first_tile)
            available_actions["select_a_tile"] = available_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action

        if self.influence_per_player[player] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"{player} does not have enough influence to use tier {tier_index} of **{self.name}**")
            return False

        slot_to_burn_from = game_action_container.required_data_for_action['slot_to_burn_from_on_red_dwarf']['slot_index']
        tile1_index = game_action_container.required_data_for_action['first_tile']
        tile2_index = game_action_container.required_data_for_action['second_tile']

        if any(index is None for index in [slot_to_burn_from, tile1_index, tile2_index]):
            await send_clients_log_message(f"Invalid disciple or tiles selected for using **{self.name}**")
            return False

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot swap a tile with itself using **{self.name}**")
            return False

        if self.slots_for_disciples[slot_to_burn_from]["color"] != player:
            await send_clients_log_message(f"Cannot burn another player's disciple on **{self.name}**")
            return False
        
        red_dwarf_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, red_dwarf_index, slot_to_burn_from)
        await send_clients_log_message(f"Used **{self.name}** to swap {game_state['tiles'][tile1_index].name} and {game_state['tiles'][tile2_index].name}")
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        return True