import game_utilities
import game_constants
from tiles.tile import Tile

class Road(Tile):
    def __init__(self):
        super().__init__(
            name="Road",
            type="Mover",
            minimum_power_to_rule=3,
            number_of_slots=7,
            power_tiers=[
                {
                    "power_to_reach_tier": 2,
                    "must_be_ruler": False,
                    "description": "**Action:** Choose a shape at an adjacent tile. Move it anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,     
                    "leader_must_be_present": False,                
                    "data_needed_for_use": ["slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": False,
                    "description": "**Action:** Same as above but choose a shape at an adjacent tile or anywhere you're present",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": ["slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
                },
                {
                    "power_to_reach_tier": 7,
                    "must_be_ruler": True,
                    "description": "**Action:** Same as above but choose any shape",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": ["slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        player_power = self.power_per_player[whose_turn_is_it]

        for i, tier in enumerate(self.power_tiers):
            if player_power >= tier["power_to_reach_tier"] and not tier["is_on_cooldown"]:
                useable_tiers.append(i)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill == "slot_and_tile_to_move_shape_from":
            slots_with_a_shape = {}
            index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            user = game_action_container.whose_action

            if tier_index == 2:
                for index, tile in enumerate(game_state["tiles"]):
                    slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_shape[index] = slots_with_shapes
            elif tier_index == 1:
                for index, tile in enumerate(game_state["tiles"]):
                    if game_utilities.determine_if_directly_adjacent(index_of_road, index) or game_utilities.has_presence(tile, user):
                        slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                        if slots_with_shapes:
                            slots_with_a_shape[index] = slots_with_shapes
            else:  # 3+ power
                adjacent_tiles = game_utilities.get_adjacent_tile_indices(index_of_road)
                for index in adjacent_tiles:
                    slots_with_shapes = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_shape[index] = slots_with_shapes

            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape
        elif current_piece_of_data_to_fill == "slot_and_tile_to_move_shape_to":
            slots_without_a_shape_per_tile = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if not slot]
                if slots_without_shapes:
                    slots_without_a_shape_per_tile[index] = slots_without_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_power = self.power_per_player[user]

        if user_power < self.power_tiers[tier_index]["power_to_reach_tier"]:
            await send_clients_log_message(f"Not enough power to use tier {tier_index} of {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False

        index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
        tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
        slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

        if tier_index == 0 and not game_utilities.determine_if_directly_adjacent(index_of_road, tile_index_from):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False

        if tier_index == 1 and not (game_utilities.determine_if_directly_adjacent(index_of_road, tile_index_from) or 
                                    game_utilities.has_presence(game_state["tiles"][tile_index_from], user)):
            await send_clients_log_message(f"Tried to use {self.name} but chose an invalid tile")
            return False

        if game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][tile_index_from].name}")
            return False

        if game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] is not None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][tile_index_to].name}")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        
        self.power_tiers[tier_index]["is_on_cooldown"] = True
        
        return True