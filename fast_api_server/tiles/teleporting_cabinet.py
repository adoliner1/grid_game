import game_utilities
import game_constants
from tiles.tile import Tile

class TeleportingCabinet(Tile):
    def __init__(self):
        super().__init__(
            name="Teleporting Cabinet",
            type="Mover",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,
                    "description": "**Action:** Choose a shape at an adjacent tile and swap it with a shape anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,             
                    "leader_must_be_present": False,        
                    "data_needed_for_use": ["slot_and_tile_to_swap_shape_from", "slot_and_tile_to_swap_shape_to"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            not self.influence_tiers[0]["is_on_cooldown"]):
            useable_tiers.append(0)
        
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill == "slot_and_tile_to_swap_shape_from":
            adjacent_slots_with_a_shape = {}
            indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["index_of_tile_in_use"])
            for index in indices_of_adjacent_tiles:
                slots_with_shapes = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_shapes) if slot]
                if slots_with_shapes:
                    adjacent_slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = adjacent_slots_with_a_shape
        elif current_piece_of_data_to_fill == "slot_and_tile_to_swap_shape_to":
            slots_with_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action

        if self.influence_per_player[user] < self.influence_tiers[tier_index]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use {self.name}")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"{self.name} is on cooldown")
            return False

        index_of_cabinet = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_from']['slot_index']
        tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_from']['tile_index']
        slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_swap_shape_to']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_cabinet, tile_index_from):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False

        if game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to swap from {game_state['tiles'][tile_index_from].name}")
            return False

        if game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to swap to {game_state['tiles'][tile_index_to].name}")
            return False

        slot_data_from = game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from]
        slot_data_to = game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to]

        await send_clients_log_message(f"Using {self.name}")

        # Swap shapes
        game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] = slot_data_to
        game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] = slot_data_from

        game_utilities.determine_influence_levels(game_state)
        game_utilities.update_presence(game_state)
        game_utilities.determine_rulers(game_state)
        await send_clients_log_message(f"Swapped {slot_data_from['shape']} from {game_state['tiles'][tile_index_from].name} with {slot_data_to['shape']} at {game_state['tiles'][tile_index_to].name}")
        
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True