import game_utilities
import game_constants
from tiles.tile import Tile

class Spear(Tile):
    def __init__(self):
        super().__init__(
            name="Spear",
            type="Attacker",
            description="3 Power, Action: Once per round, burn one of your shapes here, -2 points. Burn a shape at a tile you're present at\nRuler: Most Power, minimum 5. Don't lose points, choose a shape anywhere",
            number_of_slots=5,
            data_needed_for_use=["slot_to_burn_shape_from", "slot_and_tile_to_burn_shape_at"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.power_per_player[whose_turn_is_it] >= 3 and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action
        user_power = self.power_per_player[user]
        is_ruler = self.determine_ruler(game_state) == user

        if current_piece_of_data_to_fill_in_current_action == "slot_to_burn_shape_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, user, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_burn_shape_at":
            slots_with_a_burnable_shape = {}
            if is_ruler and user_power >= 5:
                # Ruler with 5+ power can choose any shape anywhere
                for index, tile in enumerate(game_state["tiles"]):
                    slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_burnable_shape[index] = slots_with_shapes
            else:
                # Non-ruler or ruler with less than 5 power can only choose shapes at tiles where they're present
                for index, tile in enumerate(game_state["tiles"]):
                    if game_utilities.has_presence(tile, user):
                        slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                        if slots_with_shapes:
                            slots_with_a_burnable_shape[index] = slots_with_shapes
            
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 5:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 5:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_power = self.power_per_player[user]
        is_ruler = self.determine_ruler(game_state) == user

        if user_power < 3:
            await send_clients_log_message(f"Not enough power to use {self.name}")
            return False

        index_of_spear = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_shape_from_here = game_action_container.required_data_for_action['slot_to_burn_shape_from']['slot_index']
        slot_index_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['slot_index']
        index_of_tile_to_burn_shape_at = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_at']['tile_index']

        if not is_ruler:
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

        await send_clients_log_message(f"Using {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_spear, slot_index_to_burn_shape_from_here)
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_burn_shape_at, slot_index_to_burn_shape_at)

        if not is_ruler:
            game_state["points"][user] -= 2
            await send_clients_log_message(f"{user} loses 2 points for using {self.name}")

        self.is_on_cooldown = True
        return True