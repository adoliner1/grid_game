from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile, find_index_of_tile_by_name
from tiles.tile import Tile

class Carbon(Tile):
    def __init__(self):
        super().__init__(
            name="Carbon",
            description=f"At the end of the round, per 2 circles you have here, receive a circle here. Anyone can use this tile to burn 3 of their circles here to produce a triangle\nRuling Criteria: most squares, minimum 3\nRuling Benefits: At the end of the game +10 points",
            number_of_slots=9,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        number_of_circles_current_player_has_here = 0
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it:
                number_of_circles_current_player_has_here += 1

        return number_of_circles_current_player_has_here >= 3 


    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "square":
                    red_count += 1
                elif slot["color"] == "blue" and slot["shape"] == "square":
                    blue_count += 1
        if red_count > blue_count and red_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count and blue_count >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, callback):
        red_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red" and slot["shape"] == "circle")
        blue_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue" and slot["shape"] == "circle")

        red_pairs = red_circle_count // 2
        blue_pairs = blue_circle_count // 2

        first_player = game_state["first_player"]
        second_player = 'red' if first_player == 'blue' else 'blue'

        first_player_pairs = red_pairs if first_player == 'red' else blue_pairs
        second_player_pairs = blue_pairs if first_player == 'red' else red_pairs

        for _ in range(first_player_pairs):
            await player_receives_a_shape_on_tile(game_state, first_player, self, 'circle', callback)

        for _ in range(second_player_pairs):
            await player_receives_a_shape_on_tile(game_state, second_player, self, 'circle', callback)

    async def use_tile(self, game_state, player_color, callback, **kwargs):    
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == player_color)
        
        if circle_count < 3:
            await callback(f"Not enough circles to burn on {self.name}")
            return False
        
        circles_burned = 0
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "circle" and slot["color"] == player_color:
                await self.burn_shape_at_index(game_state, i, callback)
                circles_burned += 1
                if circles_burned == 3:
                    break
        
        await callback(f"{self.name} is used")
        
        if (player_color == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'triangle', self.name, callback)
        elif (player_color == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'triangle', self.name, callback)

        return True

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await callback(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5