import game_utilities
import game_constants
from tiles.tile import Tile

class Wormhole(Tile):
    def __init__(self):
        super().__init__(
            name="Wormhole",
            type="Tile-Mover",
            description=f"At Least Two Different Shape Types: Action: Once per round, swap the position of two tiles\nRuler: Most Shapes",
            number_of_slots=3,
            data_needed_for_use=["tile1", "tile2"]
        )

    def is_useable(self, game_state):
        if self.is_on_cooldown:
            return False
        player_color = game_state["whose_turn_is_it"]
        shapes = set(slot["shape"] for slot in self.slots_for_shapes if slot and slot["color"] == player_color)
        return len(shapes) >= 2

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

        tile1_index = game_action_container.required_data_for_action['tile1']
        tile2_index = game_action_container.required_data_for_action['tile2']

        if tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid tiles selected for using {self.name}")
            return False

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for {self.name}")
            return False

        if not self.is_useable(game_state):
            await send_clients_log_message(f"Player does not have at least 2 different shapes or {self.name} is on cooldown")
            return False

        await send_clients_log_message(f"Using {self.name} to swap tiles at indices {tile1_index} and {tile2_index}")

        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        self.is_on_cooldown = True
        return True

