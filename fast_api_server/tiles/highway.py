import game_utilities
import game_constants
from tiles.tile import Tile

class Highway(Tile):
    def __init__(self):
        super().__init__(
            name="Highway",
            type="Mover",
            description="**3 Power, Action:** Once per round, ^^burn^^ one of your shapes here to move a shape on a tile to another tile\n**Ruler, Most Power, Minimum 5:** Don't ^^burn^^ a shape",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_burn_shape_from", "slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
        )

    def is_useable(self, game_state):
        if self.is_on_cooldown:
            return False

        return self.determine_ruler(game_state) == game_state["whose_turn_is_it"] or (self.power_per_player[game_state["whose_turn_is_it"]] >= 3 and game_utilities.has_presence(self, game_state["whose_turn_is_it"]))

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        if self.determine_ruler(game_state) == game_action_container.whose_action:
            game_action_container.required_data_for_action["slot_and_tile_to_burn_shape_from"] = "Ruler-Privilege"

        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_burn_shape_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_from":
            slots_with_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_to":
            slots_without_a_shape = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if not slot:
                        slots_without_shapes.append(slot_index)
                if slots_without_shapes:
                    slots_without_a_shape[index] = slots_without_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape

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
        if self.is_on_cooldown:
            await send_clients_log_message(f"Tried to use {self.name} but it's on cooldown")
            return False
        
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        if self.power_per_player[user] < 3:
            await send_clients_log_message(f"Not enough power on {self.name} to use")
            return False

        index_of_highway = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_from']['slot_index']
        slot_index_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
        index_of_tile_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
        slot_index_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        index_of_tile_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

        if user != self.determine_ruler(game_state):
            if not self.slots_for_shapes[slot_index_to_burn_shape_from]:
                await send_clients_log_message(f"Tried to use {self.name} but chose an empty slot to burn from")
                return False
            
            if self.slots_for_shapes[slot_index_to_burn_shape_from]["color"] != game_action_container.whose_action:
                await send_clients_log_message(f"Tried to use {self.name} but chose a shape owned by opponent to burn")
                return False

        if game_state["tiles"][index_of_tile_to_move_shape_from].slots_for_shapes[slot_index_to_move_shape_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_to].slots_for_shapes[slot_index_to_move_shape_to] is not None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_shape_to].name}")
            return False

        await send_clients_log_message(f"Using {self.name}")

        if user != self.determine_ruler(game_state):
            await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_highway, slot_index_to_burn_shape_from)

        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_move_shape_from, slot_index_to_move_shape_from, index_of_tile_to_move_shape_to, slot_index_to_move_shape_to)

        shape_moved = game_state['tiles'][index_of_tile_to_move_shape_to].slots_for_shapes[slot_index_to_move_shape_to]["shape"]
        color_of_shape_moved = game_state['tiles'][index_of_tile_to_move_shape_to].slots_for_shapes[slot_index_to_move_shape_to]["color"]
        await send_clients_log_message(f"Moved a {color_of_shape_moved} {shape_moved} from {game_state['tiles'][index_of_tile_to_move_shape_from].name} to {game_state['tiles'][index_of_tile_to_move_shape_to].name}")

        self.is_on_cooldown = True
        return True