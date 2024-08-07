import game_utilities
import game_constants
from tiles.tile import Tile

class Wormhole(Tile):
    def __init__(self):
        super().__init__(
            name="Wormhole",
            description=f"Once per round, anyone with a set on wormhole (1 circle, 1 square, and 1 triangle) can swap the position of two tiles. \nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game, +3 points",
            number_of_slots=9,
            data_needed_for_use=["tile1", "tile2"]
        )

    def is_useable(self, game_state):
        if self.is_on_cooldown:
            return False
        player_color = game_state["whose_turn_is_it"]
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "circle")
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "square")
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "triangle")
        return circle_count > 0 and square_count > 0 and triangle_count > 0

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill_in_current_action == "tile1":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill_in_current_action == "tile2":
            # Exclude the already selected tile1
            available_tiles = list(range(len(game_state["tiles"])))
            tile1_index = game_action_container.required_data_for_action["tile1"]
            if tile1_index is not None:
                available_tiles.remove(tile1_index)
            available_actions["select_a_tile"] = available_tiles

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

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        self.determine_ruler(game_state)
        if not self.ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False

        tile1_index = game_action_container.required_data_for_action['tile1']
        tile2_index = game_action_container.required_data_for_action['tile2']

        if tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid tiles selected for using {self.name}")
            return False

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for {self.name}")
            return False

        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == game_action_container.whose_action and slot["shape"] == "circle")
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == game_action_container.whose_action and slot["shape"] == "square")
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == game_action_container.whose_action and slot["shape"] == "triangle")

        if not (circle_count > 0 and square_count > 0 and triangle_count > 0):
            await send_clients_log_message(f"Player does not have a complete set on {self.name} to use it")
            return False

        await send_clients_log_message(f"Using {self.name} to swap tiles at indices {tile1_index} and {tile2_index}")

        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        self.is_on_cooldown = True

        return True

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3
