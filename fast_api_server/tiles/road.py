import game_utilities
import game_constants
from tiles.tile import Tile

class Road(Tile):
    def __init__(self):
        super().__init__(
            name="Road",
            type="Mover",
            description="**3 Power, Action:** Once per round, choose a shape at an adjacent tile. Move it anywhere\n**5 power:** ...choose a shape at an adjacent tile or anywhere you're present\n**7 power:** ...choose any shape\n**Ruler: Most Power**",
            number_of_slots=5,
            data_needed_for_use=["slot_and_tile_to_move_shape_from", "slot_and_tile_to_move_shape_to"]
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.power_per_player[whose_turn_is_it] >= 3 and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_from":
            slots_with_a_shape = {}
            index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            user_power = self.power_per_player[game_action_container.whose_action]

            if user_power >= 7:
                # Choose any shape
                for index, tile in enumerate(game_state["tiles"]):
                    slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_shape[index] = slots_with_shapes
            elif user_power >= 5:
                # Choose shapes at adjacent tiles or tiles where the user is present
                for index, tile in enumerate(game_state["tiles"]):
                    if game_utilities.determine_if_directly_adjacent(index_of_road, index) or game_utilities.has_presence(tile, game_action_container.whose_action):
                        slots_with_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if slot]
                        if slots_with_shapes:
                            slots_with_a_shape[index] = slots_with_shapes
            else:
                # Choose shapes only at adjacent tiles
                adjacent_tiles = game_utilities.get_adjacent_tile_indices(index_of_road)
                for index in adjacent_tiles:
                    slots_with_shapes = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_shapes) if slot]
                    if slots_with_shapes:
                        slots_with_a_shape[index] = slots_with_shapes

            available_actions["select_a_slot_on_a_tile"] = slots_with_a_shape
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_shape_to":
            slots_without_a_shape_per_tile = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_shapes = [i for i, slot in enumerate(tile.slots_for_shapes) if not slot]
                if slots_without_shapes:
                    slots_without_a_shape_per_tile[index] = slots_without_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"]:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"]:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_power = self.power_per_player[user]

        if user_power < 3:
            await send_clients_log_message(f"Not enough power to use {self.name}")
            return False

        index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
        index_of_tile_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
        slot_index_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        index_of_tile_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

        if user_power < 5 and not game_utilities.determine_if_directly_adjacent(index_of_road, index_of_tile_to_move_shape_from):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile without enough power")
            return False

        if user_power < 7 and not (game_utilities.determine_if_directly_adjacent(index_of_road, index_of_tile_to_move_shape_from) or 
                                   game_utilities.has_presence(game_state["tiles"][index_of_tile_to_move_shape_from], user)):
            await send_clients_log_message(f"Tried to use {self.name} but chose an invalid tile without enough power")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_from].slots_for_shapes[slot_index_to_move_shape_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no shape to move from {game_state['tiles'][index_of_tile_to_move_shape_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_to].slots_for_shapes[slot_index_to_move_shape_to] is not None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_shape_to].name}")
            return False

        await send_clients_log_message(f"Using {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_move_shape_from, slot_index_to_move_shape_from, index_of_tile_to_move_shape_to, slot_index_to_move_shape_to)
        self.is_on_cooldown = True
        return True