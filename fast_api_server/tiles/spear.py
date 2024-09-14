import game_utilities
import game_constants
from tiles.tile import Tile

class Spear(Tile):
    def __init__(self):
        super().__init__(
            name="Spear",
            type="Attacker",
            minimum_power_to_rule=3,
            number_of_slots=5,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "**Action:** ^^Burn^^ one of your shapes here, then ^^burn^^ a shape at a tile you're present at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                  
                    "data_needed_for_use": ["slot_to_burn_shape_from", "slot_and_tile_to_burn_shape_at"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        player_power = self.power_per_player[whose_turn_is_it]
        ruler = self.determine_ruler(game_state)

        if (player_power >= self.power_tiers[0]["power_to_reach_tier"] and 
            not self.power_tiers[0]["is_on_cooldown"] and 
            whose_turn_is_it == ruler):
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action

        if current_piece_of_data_to_fill == "slot_to_burn_shape_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, user, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill == "slot_and_tile_to_burn_shape_at":
            slots_with_a_burnable_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                if game_utilities.has_presence(tile, user):
                    slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_burnable_shape[index] = slots_with_shapes
            
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_power = self.power_per_player[user]
        ruler = self.determine_ruler(game_state)

        if user_power < self.power_tiers[tier_index]["power_to_reach_tier"]:
            await send_clients_log_message(f"Not enough power to use tier {tier_index} of {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False

        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use tier {tier_index} of {self.name}")
            return False

        index_of_spear = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_shape_from_here = game_action_container.required_data_for_action['slot_to_burn_shape_from']['slot_index']
        slot_index_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['slot_index']
        index_of_tile_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['tile_index']

        if not game_utilities.has_presence(game_state["tiles"][index_of_tile_to_burn_shape_at], user):
            await send_clients_log_message(f"Tried to use {self.name} but chose a tile where they're not present")
            return False

        if self.slots_for_shapes[slot_index_to_burn_shape_from_here] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to burn at {self.name}")
            return False

        if game_state["tiles"][index_of_tile_to_burn_shape_at].slots_for_shapes[slot_index_to_burn_shape_at] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape_at].name}")
            return False

        if self.slots_for_shapes[slot_index_to_burn_shape_from_here]["color"] != user:
            await send_clients_log_message(f"Tried to use {self.name} but chose a shape that didn't belong to them")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_spear, slot_index_to_burn_shape_from_here)
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_shape_at, slot_index_to_burn_shape_at)

        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True