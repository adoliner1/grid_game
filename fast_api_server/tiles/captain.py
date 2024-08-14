import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Captain(Tile):
    def __init__(self):
        super().__init__(
            name="Captain",
            description=f"Ruling Criteria: at least 2 shapes total, at least 1 square, tiebreaker most shapes \nRuling Benefits: Once per round, when you receive a shape at an adjacent tile, you may burn a shape anywhere",
            number_of_slots=5,
        )

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        slots_with_a_burnable_shape = {}
        for tile_index, tile in enumerate(game_state["tiles"]):
            slots_with_shapes = []
            for slot_index, slot in enumerate(tile.slots_for_shapes):
                if slot:
                    slots_with_shapes.append(slot_index)
            if slots_with_shapes:
                slots_with_a_burnable_shape[tile_index] = slots_with_shapes
        available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        red_square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red" and slot["shape"] == "square")
        blue_square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue" and slot["shape"] == "square")

        if red_count >= 2 and red_square_count >= 1 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 2 and blue_square_count >= 1 and blue_count > red_count:
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

        if self.is_on_cooldown:
            await send_clients_log_message(f"{self.name} is on cooldown")
            return False

        slot_index_to_burn_shape = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape']['slot_index']
        index_of_tile_to_burn_shape = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape']['tile_index']

        if game_state["tiles"][index_of_tile_to_burn_shape].slots_for_shapes[slot_index_to_burn_shape] == None:
            await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape].name} at slot {slot_index_to_burn_shape}")
            return False

        await send_clients_log_message(f"Reacting with {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_tile_to_burn_shape, slot_index_to_burn_shape)
        
        self.is_on_cooldown = True
        return True
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')
        index_of_captain = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if not game_utilities.determine_if_directly_adjacent(index_of_captain, index_of_tile_received_at):
            return

        ruler = self.determine_ruler(game_state)
        if ruler != receiver:
            return

        if self.is_on_cooldown:
            return
        
        await send_clients_log_message(f"{self.ruler} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="react_with_tile",
                required_data_for_action={"slot_and_tile_to_burn_shape": {}, "index_of_tile_being_reacted_with": index_of_captain},
                whose_action=receiver,
                is_a_reaction=True,
            )
    
        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()
