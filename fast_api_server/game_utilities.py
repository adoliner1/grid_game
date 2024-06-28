async def produce_shape_for_player(game_state, player_color, amount, shape_type, callback=None):

    game_state["shapes"][player_color][f"number_of_{shape_type}s"] += amount

    if callback:
        await callback(f"Produced {amount} {shape_type}(s) for {player_color} player")

async def player_receives_a_shape_on_tile(game_state, player_color, tile, shape_type, callback=None):
    next_empty_slot = tile.slots_for_shapes.index(None)

    if next_empty_slot == None:
        await callback(f"{player_color} cannot receive a {shape_type} on {tile.name}, no empty slots")
    else:
        tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
        await callback(f"{player_color} receives a {shape_type} on {tile.name}")
