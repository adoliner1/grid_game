from game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile, find_index_of_tile_by_name, determine_if_directly_adjacent
from tiles.tile import Tile

class Sword(Tile):
    def __init__(self):
        super().__init__(
            name="Sword",
            description = f"Ruling Criteria: Most shapes, minimum 3\nRuling Benefits: You may use this tile to burn one of your shapes here and a shape on an adjacent tile",
            number_of_slots=5,
            has_use_action_for_ruler = True,
            data_needed_for_use_with_selectors={"slot_and_tile_to_burn_shape_from":  ["slot", "user-color", "calling-tile", "non-empty"],
                                 "slot_and_tile_to_burn_shape_at": ["slot", "adjacent-to_calling-tile", "non-empty"]}
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
        slot_to_burn_shape_from_here = kwargs.get('slot_and_tile_to_burn_shape_from').get('slot')
        slot_to_burn_shape_at = kwargs.get('slot_and_tile_to_burn_shape_at').get('slot')
        index_of_tile_to_burn_shape_at = kwargs.get('slot_and_tile_to_burn_shape_at').get('tile')

        if not determine_if_directly_adjacent(index_of_sword, index_of_tile_to_burn_shape_at):
            await callback(f"Tried to use {self.name} but chose a non-adjacent tile")
            return
        
        if self.slots_for_shapes[slot_to_burn_shape_from_here] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to burn at {self.name}")
            return
        
        if game_state["tiles"][index_of_tile_to_burn_shape_at].slots_for_shapes[slot_to_burn_shape_at] == None:
            await callback(f"Tried to use {self.name} but chose a slot with no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape_at].name}")
            return

        if self.slots_for_shapes[slot_to_burn_shape_from_here]["color"] != self.ruler:
            await callback(f"Tried to use {self.name} but chose shape that didn't belong to them at {self.name}")
            return
        
        await callback(f"Using {self.name}")
        await self.burn_shape_at_index(game_state, slot_to_burn_shape_from_here, callback)
        await game_state["tiles"][index_of_tile_to_burn_shape_at].burn_shape_at_index(game_state, slot_to_burn_shape_at, callback)