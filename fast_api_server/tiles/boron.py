from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Boron(Tile):
    def __init__(self):
        super().__init__(
            name="Boron",
            description = f"At the end of the round, if you have a square here, receive a circle here\nRuling Criteria: 7 or more circles \nRuling Benefits: At the end of round: produce 1 triangle. At the end of the game: 2vp",
            number_of_slots=11,
        )

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "circle":
                    red_count += 1
                elif slot["color"] == "blue" and slot["shape"] == "circle":
                    blue_count += 1
        if red_count >= 7:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 7:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'triangle', callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'triangle', callback)

    async def end_of_round_effect(self, game_state, callback):

        red_has_square = False
        blue_has_square = False
        
        for slot in self.slots_for_shapes:
                
            if slot:
                if slot["color"] == "red" and slot["shape"] == "square":
                    red_has_square = True
                elif slot["color"] == "blue" and slot["shape"] == "square":
                    blue_has_square = True

        if red_has_square and blue_has_square:
            await callback(f"both players have a square on {self.name}")
            first_player = game_state["first_player"]
            second_player = 'red' if first_player == 'blue' else 'blue'
            await player_receives_a_shape_on_tile(game_state, first_player, self, 'circle', callback)
            await player_receives_a_shape_on_tile(game_state, second_player, self, 'circle', callback)
        
        elif red_has_square:
            await player_receives_a_shape_on_tile(game_state, 'red', self, 'circle', callback)
            await callback(f"red has a square on {self.name}")
        elif blue_has_square:
            await callback(f"blue has a square on {self.name}")
            await player_receives_a_shape_on_tile(game_state, 'blue', self, 'circle', callback)

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await callback(f"Boron gives 2 points to {ruler}")
            game_state["points"][ruler] += 2
