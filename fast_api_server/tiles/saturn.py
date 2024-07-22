from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Saturn(Tile):
    def __init__(self):
        super().__init__(
            name="Saturn",
            description = f"Ruling Criteria: 3 or more shapes\nRuling Benefits: You may use this tile to burn one of your triangles here to produce 3 squares",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "triangle" and slot["color"] == ruler:
                return True
        
        return False

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
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
        
        triangle_found = False
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "triangle" and slot["color"] == ruler:
                await callback(f"{self.name} is used")                
                await self.burn_shape_at_index(game_state, i, callback)
                triangle_found = True
                break
        
        if not triangle_found:
            await callback(f"No triangle to burn on {self.name}")
            return False
        
        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 3, 'square', self.name, callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 3, 'square', self.name, callback)

        return True
