import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Conductor(Tile):
    def __init__(self):
        super().__init__(
            name="Conductor",
            type="Mover",
            description="Ruler: Most Shapes, Reaction: Once per round, when you receive a shape, you may move it to a tile adjacent to Conductor",
            number_of_slots=5,
            is_on_cooldown=False
        )

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        slots_without_a_shape_per_tile = {}
        for index, tile in enumerate(game_state["tiles"]):
            if game_utilities.determine_if_directly_adjacent(game_utilities.find_index_of_tile_by_name(game_state, self.name), index):
                slots_without_shapes = [slot_index for slot_index, slot in enumerate(tile.slots_for_shapes) if not slot]
                if slots_without_shapes:
                    slots_without_a_shape_per_tile[index] = slots_without_shapes
        available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile

    async def react(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        
        if not ruler or ruler != game_action_container.whose_action or self.is_on_cooldown:
            await send_clients_log_message(f"Cannot react with {self.name}")
            return False

        index_of_conductor = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
        tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
        slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_conductor, tile_index_to):
            await send_clients_log_message(f"Tried to react with {self.name} but destination tile isn't adjacent")
            return False

        if game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] is None:
            await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to move")
            return False

        if game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] is not None:
            await send_clients_log_message(f"Tried to react with {self.name} but chose a non-empty slot to move to")
            return False

        await send_clients_log_message(f"Reacting with {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        self.is_on_cooldown = True
        return True

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')
        index_of_slot_received_at = data.get('index_of_slot_received_at')
        
        ruler = self.determine_ruler(game_state)
        if ruler != receiver or self.is_on_cooldown:
            return

        await send_clients_log_message(f"{ruler} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="react_with_tile",
            required_data_for_action={
                "slot_and_tile_to_move_shape_from": {"slot_index": index_of_slot_received_at, "tile_index": index_of_tile_received_at},
                "slot_and_tile_to_move_shape_to": {},
                "index_of_tile_being_reacted_with": game_utilities.find_index_of_tile_by_name(game_state, self.name)
            },
            whose_action=receiver,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.is_on_cooldown = False