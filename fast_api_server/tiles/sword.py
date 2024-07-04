from fast_api_server.game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile, find_index_of_tile_by_name, determine_if_directly_adjacent
from fast_api_server.tiles.tile import Tile

class Sword(Tile):
    def __init__(self):
        super().__init__(
            name="sword",
            description = f"Ruling Criteria: most shapes, minimum 3\nRuling Benefits: You may use this tile to burn one of your shapes here and any shape on any adjacent tile",
            number_of_slots=5,
            has_use_action_for_ruler = True,
            data_needed_for_use={"slot_to_burn_shape_from_here":  ["slot", "user-color", "calling-tile", "non-empty"],
                                 "slot_to_burn_shape_at_tile_to_burn_shape_on": ["slot", "adjacent-to_calling-tile", "non-empty"] }
        )

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
        self.determine_ruler(game_state)
        if not self.ruler:
            await callback(f"No ruler determined for {self.name} cannot use")
            return
        
        if self.ruler != player_color:
            await callback(f"Non-ruler tried to use {self.name}")
            return
        
        index_of_sword = find_index_of_tile_by_name(game_state, self.name)
        slot_to_burn_shape_from_here = kwargs.get('slot_to_burn_shape_from_here')
        index_of_tile_to_burn_shape_on = kwargs.get('index_of_tile_to_burn_shape_on')
        slot_to_burn_shape_at_tile_to_burn_shape_on = kwargs.get('tile_to_burn_shape_on')

        if not determine_if_directly_adjacent(index_of_sword, index_of_tile_to_burn_shape_on):
            await callback(f"Tried to use {self.name} but chose a non-adjacent tile")
            return
        
        if self.slots_for_shapes[slot_to_burn_shape_from_here] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to burn at {self.name}")
            return
        
        if game_state["tiles"][index_of_tile_to_burn_shape_on]["slots_for_shapes"][slot_to_burn_shape_at_tile_to_burn_shape_on] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape_on].name}")
            return

        if self.slots_for_shapes[slot_to_burn_shape_from_here]["color"] != self.ruler:
            await callback(f"Tried to use {self.name} but chose shape of the wrong color at {self.name}")
            return
        
        await callback(f"Using {self.name}")
        self.burn_shape_at_index(game_state, slot_to_burn_shape_from_here, callback)
        game_state["tiles"][index_of_tile_to_burn_shape_on].burn_shape_at_index(game_state, slot_to_burn_shape_at_tile_to_burn_shape_on, callback)
        