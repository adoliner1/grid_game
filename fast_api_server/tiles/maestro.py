import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Maestro(Tile):
    def __init__(self):
        super().__init__(
            name="Maestro",
            type="Mover",
            description="Ruler: Most shapes, Reaction: Once per round, when you receive a shape, you may move it to a tile adjacent to the tile you received it at",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        
        if red_shapes > blue_shapes:
            self.ruler = 'red'
            return 'red'
        elif blue_shapes > red_shapes:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        index_of_tile_received_at = game_action_container.required_data_for_action.get('index_of_tile_received_at')
        if index_of_tile_received_at is not None:
            adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_state, index_of_tile_received_at)
            slots_without_a_shape_per_tile = {}
            for index in adjacent_tiles:
                slots_without_shapes = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_shapes) if not slot]
                if slots_without_shapes:
                    slots_without_a_shape_per_tile[index] = slots_without_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile

    async def react(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        if not ruler or ruler != game_action_container.whose_action or self.is_on_cooldown:
            await send_clients_log_message(f"Cannot react with {self.name}")
            return False

        index_of_tile_received_at = game_action_container.required_data_for_action['index_of_tile_received_at']
        slot_index_received_at = game_action_container.required_data_for_action['slot_index_received_at']
        slot_index_to_move_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        index_of_tile_to_move_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(index_of_tile_received_at, index_of_tile_to_move_to):
            await send_clients_log_message(f"Tried to react with {self.name} but destination tile isn't adjacent to the tile where the shape was received")
            return False

        await send_clients_log_message(f"Reacting with {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_received_at, slot_index_received_at, index_of_tile_to_move_to, slot_index_to_move_to)
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
                "index_of_tile_being_reacted_with": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tile_received_at": index_of_tile_received_at,
                "slot_index_received_at": index_of_slot_received_at,
                "slot_and_tile_to_move_shape_to": {}
            },
            whose_action=receiver,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()