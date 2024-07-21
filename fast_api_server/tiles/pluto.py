from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Pluto(Tile):
    def __init__(self):
        super().__init__(
            name="Pluto",
            description = f"Ruling Criteria: 3 or more circles\nRuling Benefits: You may use this tile to burn one of your circles here to produce a square. At the end of the game +2 points",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        for slot in self.slots_for_shapes:
            if slot["shape"] == "circle" and slot["color"] == ruler:
                return True
        
        return False

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "circle":
                    red_count += 1
                elif slot["color"] == "blue" and slot["shape"] == "circle":
                    blue_count += 1
        if red_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 3:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def use_tile(self, game_state, player_color, callback, **kwargs):
        ruler = self.determine_ruler(game_state)
        if not ruler:
            await callback(f"No ruler determined for {self.name} cannot use")
            return False
        
        if ruler != player_color:
            await callback(f"Non-ruler tried to use {self.name}")
            return False
        
        circle_found = False
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "circle" and slot["color"] == ruler:
                await callback(f"{self.name} is used")                
                await self.burn_shape_at_index(game_state, i, callback)
                circle_found = True
                break
        
        if not circle_found:
            await callback(f"No circle to burn on {self.name}")
            return False
        
        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'square', self.name, callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'square', self.name, callback)

        return True

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await callback(f"Pluto gives 2 points to {ruler}")
            game_state["points"][ruler] += 2