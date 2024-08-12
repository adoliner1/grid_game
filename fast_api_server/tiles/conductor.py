import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Conductor(Tile):
    def __init__(self):
        super().__init__(
            name="Conductor",
            description=f"Ruling Criteria: most shapes, minimum 2\nRuling Benefits: When you receive a shape at an adjacent tile, you may move it to an empty slot anywhere",
            number_of_slots=5,
        )

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        #only thing to fill here ever is slot_and_tile_to_move_shape_to
        slots_without_a_shape_per_tile = {}
        for index, tile in enumerate(game_state["tiles"]):
            slots_without_shapes = []
            for slot_index, slot in enumerate(tile.slots_for_shapes):
                if not slot:
                    slots_without_shapes.append(slot_index)
            if slots_without_shapes:
                slots_without_a_shape_per_tile[index] = slots_without_shapes
        available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile
    
    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count >= 2 and  red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 2 and blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def react(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot react")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to react with {self.name}")
            return False

        index_of_conductor = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
        index_of_tile_to_move_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
        slot_index_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
        index_of_tile_to_move_shape_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']
        shape_to_move = game_state['tiles'][index_of_tile_to_move_shape_from].slots_for_shapes[slot_index_to_move_shape_from]["shape"]

        if not game_utilities.determine_if_directly_adjacent(index_of_conductor, index_of_tile_to_move_shape_from):
            await send_clients_log_message(f"Tried to react with {self.name} but tile's aren't adjacent")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_from].slots_for_shapes[slot_index_to_move_shape_from] == None:
            await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to move from {game_state['tiles'][index_of_tile_to_move_shape_from].name} at slot {slot_index_to_move_shape_from}")
            return False

        if game_state["tiles"][index_of_tile_to_move_shape_to].slots_for_shapes[slot_index_to_move_shape_to] != None:
            await send_clients_log_message(f"Tried to react with {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_shape_to].name}")
            return False

        await send_clients_log_message(f"Reacting with {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_move_shape_from, slot_index_to_move_shape_from, index_of_tile_to_move_shape_to, slot_index_to_move_shape_to)
        return True
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):

        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')
        index_of_slot_received_at = data.get('index_of_slot_received_at')
        index_of_conductor = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if not game_utilities.determine_if_directly_adjacent(index_of_conductor, index_of_tile_received_at):
            return

        ruler = self.determine_ruler(game_state)
        if ruler != receiver:
            return
        
        await send_clients_log_message(f"{self.ruler} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="react_with_tile",
                required_data_for_action={"slot_and_tile_to_move_shape_from": {"slot_index": index_of_slot_received_at, "tile_index": index_of_tile_received_at}, "slot_and_tile_to_move_shape_to": {}, "index_of_tile_being_reacted_with": index_of_conductor},
                whose_action=receiver,
                is_a_reaction=True,
            )
    
        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()