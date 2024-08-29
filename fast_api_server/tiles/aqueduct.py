import game_utilities
import game_constants
from tiles.tile import Tile

class Aqueduct(Tile):
    def __init__(self):
        super().__init__(
            name="Aqueduct",
            type="Mover",
            description=f"**Ruler, Most Power, Minimum 3, Action:** Once per round, ^^burn^^ one of your shapes here. Choose a shape at a tile you're present at. Move as many of that shape type and color as possible to another tile you're present at",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_burn_shape_from", "slot_and_tile_to_move_shapes_from", "tile_to_move_shapes_to"]
        )

    def is_useable(self, game_state):
        return not self.is_on_cooldown and self.determine_ruler(game_state) == game_state["whose_turn_is_it"] or (self.power_per_player[game_state["whose_turn_is_it"]] >= 3 and game_utilities.has_presence(self, game_state["whose_turn_is_it"]))

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_burn_shape_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_shape_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shapes_from":
            slots_with_a_shape_on_a_tile_user_has_presence = {}
            indices_of_tiles_where_user_has_presence = game_utilities.get_tile_indices_where_player_has_presence(game_state, game_action_container.whose_action)
            for index in indices_of_tiles_where_user_has_presence:
                slots_with_shapes = []
                for slot_index, slot in enumerate(game_state["tiles"][index].slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape_on_a_tile_user_has_presence[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape_on_a_tile_user_has_presence
        elif current_piece_of_data_to_fill_in_current_action == "tile_to_move_shapes_to":
            indices_of_tiles_where_user_has_presence = game_utilities.get_tile_indices_where_player_has_presence(game_state, game_action_container.whose_action)
            available_actions["select_a_tile"] = indices_of_tiles_where_user_has_presence

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 3:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        if self.determine_ruler != user:
            await send_clients_log_message(f"Tried to use {self.name} without being the ruler")
            return False            

        index_of_aqueduct = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_shape_from_here = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_from']['slot_index']
        slot_index_to_move_shapes_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shapes_from']['slot_index']
        index_of_tile_to_move_shapes_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shapes_from']['tile_index']
        index_of_tile_to_move_shapes_to = game_action_container.required_data_for_action['tile_to_move_shapes_to']
        shape_to_move = game_state['tiles'][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from]["shape"]
        color_of_shape_to_move = game_state['tiles'][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from]["color"]

        if not user == self.determine_ruler(game_state):
            if not self.slots_for_shapes[slot_index_to_burn_shape_from_here]:
                await send_clients_log_message(f"Tried to use {self.name} but chose an empty slot to burn from")
                return False
            
            if self.slots_for_shapes[slot_index_to_burn_shape_from_here]["color"] != game_action_container.whose_action:
                await send_clients_log_message(f"Tried to use {self.name} but chose a shape owned by opponent to burn")
                return False

            if game_state["tiles"][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from] is None:
                await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shapes_from].name}")
                return False

            await send_clients_log_message(f"Using {self.name}")

            await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_aqueduct, slot_index_to_burn_shape_from_here)
            
            # Move as many shapes as possible from the source tile to the destination tile
            slots_to_fill = [i for i, slot in enumerate(game_state["tiles"][index_of_tile_to_move_shapes_to].slots_for_shapes) if not slot]
            shapes_to_move = [i for i, slot in enumerate(game_state["tiles"][index_of_tile_to_move_shapes_from].slots_for_shapes) if slot and slot["shape"] == shape_to_move and slot["color"] == color_of_shape_to_move]

            moves = min(len(slots_to_fill), len(shapes_to_move))
            for _ in range(moves):
                slot_index_to_fill = slots_to_fill.pop(0)
                slot_index_to_move = shapes_to_move.pop(0)
                await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_move_shapes_from, slot_index_to_move, index_of_tile_to_move_shapes_to, slot_index_to_fill)
            
            await send_clients_log_message(f"Moved {moves} {color_of_shape_to_move} {shape_to_move}(s) from {game_state['tiles'][index_of_tile_to_move_shapes_from].name} to {game_state['tiles'][index_of_tile_to_move_shapes_to].name}")
            return True
        
        else:
            if game_state["tiles"][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from] is None:
                await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shapes_from].name}")
                return False

            await send_clients_log_message(f"Using {self.name}")
            
            # Move as many shapes as possible from the source tile to the destination tile
            slots_to_fill = [i for i, slot in enumerate(game_state["tiles"][index_of_tile_to_move_shapes_to].slots_for_shapes) if not slot]
            shapes_to_move = [i for i, slot in enumerate(game_state["tiles"][index_of_tile_to_move_shapes_from].slots_for_shapes) if slot and slot["shape"] == shape_to_move and slot["color"] == color_of_shape_to_move]

            moves = min(len(slots_to_fill), len(shapes_to_move))
            for _ in range(moves):
                slot_index_to_fill = slots_to_fill.pop(0)
                slot_index_to_move = shapes_to_move.pop(0)
                await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_move_shapes_from, slot_index_to_move, index_of_tile_to_move_shapes_to, slot_index_to_fill)
            
            await send_clients_log_message(f"Moved {moves} {color_of_shape_to_move} {shape_to_move}(s) from {game_state['tiles'][index_of_tile_to_move_shapes_from].name} to {game_state['tiles'][index_of_tile_to_move_shapes_to].name}")
            return True