import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Plains(Tile):
    def __init__(self):
        super().__init__(
            name="Plains",
            type="Producer/Scorer",
            description="Ruler: Most shapes, minimum 2. When a tile produces shapes, you may receive a circle at a tile adjacent to it",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
       
        if red_shapes > blue_shapes and red_shapes >= 2:
            self.ruler = 'red'
            return 'red'
        elif blue_shapes > red_shapes and blue_shapes >= 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_produce"][self.name] = self.on_produce_effect

    async def on_produce_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        producing_tile_name = data.get('producing_tile_name')
        producing_player = data.get('producing_player')
        ruler = self.determine_ruler(game_state)
        if not ruler or ruler != producing_player:
            return

        producing_tile_index = game_utilities.find_index_of_tile_by_name(game_state, producing_tile_name)
        plains_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        adjacent_tiles = game_utilities.get_adjacent_tile_indices(producing_tile_index)
        available_tiles = [tile_index for tile_index in adjacent_tiles if tile_index != plains_index]

        if not available_tiles:
            return

        await send_clients_log_message(f"{ruler} may receive a circle at a tile adjacent to {producing_tile_name} due to {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="react_with_tile",
            required_data_for_action={
                "tile_to_receive_circle": {},
                "index_of_tile_being_reacted_with": plains_index
            },
            whose_action=ruler,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        producing_tile_index = game_action_container.required_data_for_action.get('producing_tile_index')
        if producing_tile_index is not None:
            adjacent_tiles = game_utilities.get_adjacent_tile_indices(producing_tile_index)
            plains_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            available_tiles = [tile_index for tile_index in adjacent_tiles if tile_index != plains_index]
            available_actions["select_a_tile"] = available_tiles

    async def react(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to react with {self.name}")
            return False

        tile_to_receive_circle = game_action_container.required_data_for_action['tile_to_receive_circle']
        
        await game_utilities.player_receives_a_shape_on_tile(
            game_state,
            game_action_container_stack,
            send_clients_log_message,
            send_clients_available_actions,
            send_clients_game_state,
            ruler,
            game_state["tiles"][tile_to_receive_circle],
            "circle"
        )
        
        await send_clients_log_message(f"{ruler} receives a circle at {game_state['tiles'][tile_to_receive_circle].name} due to {self.name}")
        return True