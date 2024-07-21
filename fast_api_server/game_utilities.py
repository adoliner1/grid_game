async def produce_shape_for_player(game_state, player_color, amount, shape_type, calling_tile_name, callback=None):

    game_state["shapes_in_storage"][player_color][shape_type] += amount

    for listener_name, listener_function in game_state["listeners"]["on_produce"].items():
        await listener_function(game_state, callback, amount_produced=amount, producer=player_color, shape=shape_type, producing_tile_name=calling_tile_name)

    if callback:
        if calling_tile_name:
            await callback(f" {calling_tile_name} produced {amount} {shape_type}(s) for {player_color}")
        else:
            await callback(f" {player_color} produced {amount} {shape_type}(s)")            

async def player_receives_a_shape_on_tile(game_state, player_color, tile, shape_type, callback=None):

    if None not in tile.slots_for_shapes:
        await callback(f"{player_color} cannot receive a {shape_type} on {tile.name}, no empty slots")
        return
    
    next_empty_slot = tile.slots_for_shapes.index(None)
    tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
    await callback(f"{player_color} receives a {shape_type} on {tile.name}")

def get_other_player_color(player_color):
    return 'blue' if player_color == 'red' else 'red'

def determine_rulers(game_state):
    for tile in game_state["tiles"]:
        tile.determine_ruler(game_state)

def find_index_of_tile_by_name(game_state, name):
    for index, tile in enumerate(game_state["tiles"]):
        if tile.name == name:
            return index
    return None

def determine_if_directly_adjacent(index1, index2):
    if index1 < 0 or index1 > 8 or index2 < 0 or index2 > 8:
        return False

    row1, col1 = divmod(index1, 3)
    row2, col2 = divmod(index2, 3)

    if row1 == row2 and abs(col1 - col2) == 1:
        return True

    if col1 == col2 and abs(row1 - row2) == 1:
        return True

    return False

def count_number_of_shape_for_player_on_tile(shape, player, tile):
    count = 0
    for slot in tile.slots_for_shapes:
        if slot and slot["shape"] == shape and slot["color"] == player:
            count += 1
    return count

def determine_how_many_full_rows_player_rules(game_state, player):
    full_rows = 0
    for row in range(3):
        player_rules_row = True
        for col in range(3):
            tile_index = row * 3 + col
            tile = game_state["tiles"][tile_index]
            if tile.ruler != player:
                player_rules_row = False
                break
        if player_rules_row:
            full_rows += 1

    return full_rows

def determine_how_many_full_columns_player_rules(game_state, player):
    full_columns = 0

    for col in range(3):
        player_rules_column = True
        for row in range(3):
            tile_index = row * 3 + col
            tile = game_state["tiles"][tile_index]
            if tile.ruler != player:
                player_rules_column = False
                break  # Exit the inner loop and move to the next column
        if player_rules_column:
            full_columns += 1

    return full_columns

#returns a dict where the keys are tile indices and the associated list are the indices of the slots on that tile that can be placed on
def get_slots_that_can_be_placed_on(game_state, shape_type):
    shape_hierarchy = {
        "circle": 1,
        "square": 2,
        "triangle": 3
    }
    
    shape_strength = shape_hierarchy.get(shape_type)
    slots_that_can_be_placed_on = {}

    for tile_index, tile in enumerate(game_state["tiles"]):
        slots_for_tile = []
        for slot_index, slot in enumerate(tile.slots_for_shapes):
            if slot is None or shape_hierarchy.get(slot["shape"]) < shape_strength:
                slots_for_tile.append(slot_index)
        if slots_for_tile:
            slots_that_can_be_placed_on[tile_index] = slots_for_tile
    
    return slots_that_can_be_placed_on

def get_slots_with_a_shape_of_player_color_at_tile_index(game_state, player_color, tile_index):
    slots_with_shape = []
    tile = game_state["tiles"][tile_index]
    
    for slot_index, slot in enumerate(tile.slots_for_shapes):
        if slot and slot["color"] == player_color:
            slots_with_shape.append(slot_index)
    
    return slots_with_shape

def get_adjacent_tile_indices(tile_index):
    adjacent_indices = []
    # Determine row and column of the current tile
    row, col = divmod(tile_index, 3)
    
    # Check for adjacent tiles
    if row > 0:  # Not in the first row, can have a tile above
        adjacent_indices.append(tile_index - 3)
    if row < 2:  # Not in the last row, can have a tile below
        adjacent_indices.append(tile_index + 3)
    if col > 0:  # Not in the first column, can have a tile to the left
        adjacent_indices.append(tile_index - 1)
    if col < 2:  # Not in the last column, can have a tile to the right
        adjacent_indices.append(tile_index + 1)
    
    return adjacent_indices
