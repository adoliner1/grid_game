import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Maestro(Tile):
    def __init__(self):
        super().__init__(
            name="Maestro",
            description=f"Ruling Criteria: most shapes\nRuling Benefits: When you receive a shape at an adjacent tile, you may burn a circle here to gain 3 points",
            number_of_slots=5,
        )

    def set_available_actions_for_reaction(self, game_state, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        index_of_maestro = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        #selecting maestro means "Yes I want to use maestro" right now
        available_actions["select_a_tile"] = [index_of_maestro]

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")

        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def has_ruler_circle(self):
        return any(slot for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == self.ruler)

    async def react(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot react")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to react with {self.name}")
            return False

        if not self.has_ruler_circle():
            await send_clients_log_message(f"No circle available to burn on {self.name}")
            return False

        index_of_maestro = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        # Find the first available circle to burn
        slot_index_to_burn_circle = next(
            (i for i, slot in enumerate(self.slots_for_shapes) 
             if slot and slot["shape"] == "circle" and slot["color"] == self.ruler),
            None
        )

        await send_clients_log_message(f"Reacting with {self.name}")
        saved_ruler = self.ruler
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_maestro, slot_index_to_burn_circle)
        game_state["points"][saved_ruler] += 3
        await send_clients_log_message(f"{saved_ruler} gains 3 points from using {self.name}")

        return True
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')
        index_of_maestro = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if not game_utilities.determine_if_directly_adjacent(index_of_maestro, index_of_tile_received_at):
            return

        ruler = self.determine_ruler(game_state)
        if ruler != receiver:
            return

        if not self.has_ruler_circle():
            return
        
        await send_clients_log_message(f"{self.ruler} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
                event=asyncio.Event(),
                game_action="react_with_tile",
                required_data_for_action={"index_of_tile_being_reacted_with": index_of_maestro, "use_maestro_decision": None},
                whose_action=receiver,
                is_a_reaction=True,
            )
    
        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()