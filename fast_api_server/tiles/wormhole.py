from game_utilities import move_shape, find_index_of_tile_by_name
from tiles.tile import Tile

class Wormhole(Tile):
    def __init__(self):
        super().__init__(
            name="Wormhole",
            description=f"Anyone with a set on wormhole (1 circle, 1 square, and 1 triangle) can use Wormhole to swap the position of two tiles. This puts wormhole on cooldown. \nRuling Criteria: Most shapes\nRuling Benefits: At the end of the game, +3 points",
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

    def set_available_actions(self, game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        if current_piece_of_data_to_fill_in_current_action == "tile1":
            available_actions_with_details["select_a_tile"] = list(range(len(game_state["tiles"])))
        elif current_piece_of_data_to_fill_in_current_action == "tile2":
            # Exclude the already selected tile1
            available_tiles = list(range(len(game_state["tiles"])))
            tile1_index = current_action.get("tile1")
            if tile1_index is not None:
                available_tiles.remove(tile1_index)
            available_actions_with_details["select_a_tile"] = available_tiles

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

    async def use_tile(self, game_state, player_color, callback, **kwargs):
        self.determine_ruler(game_state)
        if not self.ruler:
            await callback(f"No ruler determined for {self.name} cannot use")
            return False
        
        if self.ruler != player_color:
            await callback(f"Non-ruler tried to use {self.name}")
            return False

        index_of_wormhole = find_index_of_tile_by_name(game_state, self.name)
        tile1_index = kwargs.get('tile1')
        tile2_index = kwargs.get('tile2')

        if tile1_index is None or tile2_index is None:
            await callback(f"Invalid tiles selected for using {self.name}")
            return False

        if tile1_index == tile2_index:
            await callback(f"Cannot select the same tile twice for {self.name}")
            return False

        # Check if the player has a set on Wormhole
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "circle")
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "square")
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "triangle")

        if not (circle_count > 0 and square_count > 0 and triangle_count > 0):
            await callback(f"Player does not have a complete set on {self.name} to use it")
            return False

        await callback(f"Using {self.name} to swap tiles at indices {tile1_index} and {tile2_index}")

        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]

        # Put Wormhole on cooldown
        self.is_on_cooldown = True

        return True

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await callback(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3
