from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile
from tiles.tile import Tile

class Pluto(Tile):
    def __init__(self):
        super().__init__(
            name="Pluto",
            description = "Ruling Criteria: most shapes\nRuling Benefits: You may use this tile to burn 2 circles here to produce a square. At the end of the game +3 points",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == ruler)
        return circle_count >= 2

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
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
        
        circles_to_burn = [
            i for i, slot in enumerate(self.slots_for_shapes)
            if slot and slot["shape"] == "circle" and slot["color"] == ruler
        ]

        if len(circles_to_burn) < 2:
            await callback(f"Not enough circles to burn on {self.name}")
            return False
        
        for i in circles_to_burn[:2]:
            await self.burn_shape_at_index(game_state, i, callback)

        await callback(f"{self.name} is used")
        
        await produce_shape_for_player(game_state, player_color, 1, 'square', self.name, callback)
        return True

    async def end_of_game_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await callback(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3
