import game_utilities
import game_constants
from tiles.tile import Tile

class Aqueduct(Tile):
    def __init__(self):
        super().__init__(
            name="Aqueduct",
            description=f"Ruling Criteria: 2 or more shapes\nRuling Benefits: Burn all your shapes here. Choose a shape at a tile. Move as many of that colored shape as possible to a tile anywhere.",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_move_shapes_from", "tile_to_move_shapes_to"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shapes_from":
            slots_with_a_shape = {}
            indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["index_of_tile_in_use"])
            for index in indices_of_adjacent_tiles:
                slots_with_shapes = []
                for slot_index, slot in enumerate(game_state["tiles"][index].slots_for_shapes):
                    if slot:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_shape[index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "tile_to_move_shapes_to":
            all_tiles = [index for index, tile in enumerate(game_state["tiles"])]
            available_actions["select_a_tile"] = all_tiles

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count >= 2 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 2 and blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False

        index_of_aqueduct = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_move_shapes_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shapes_from']['slot_index']
        index_of_tile_to_move_shapes_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shapes_from']['tile_index']
        index_of_tile_to_move_shapes_to = game_action_container.required_data_for_action['tile_to_move_shapes_to']
        shape_to_move = game_state['tiles'][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from]["shape"]
        color_of_shape_to_move = game_state['tiles'][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from]["color"]

        if game_state["tiles"][index_of_tile_to_move_shapes_from].slots_for_shapes[slot_index_to_move_shapes_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shapes_from].name}")
            return False

        await send_clients_log_message(f"Using {self.name}")

        # Burn all shapes on Aqueduct
        color_to_burn = self.ruler
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == color_to_burn:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_aqueduct, i)
        
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
