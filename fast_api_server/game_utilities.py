import asyncio
import game_action_container
import game_constants

#async

async def place_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, slot_index, shape, color):
    tile_to_place_on = game_state["tiles"][tile_index]
    old_shape =  tile_to_place_on.slots_for_shapes[slot_index]
    tile_to_place_on.slots_for_shapes[slot_index] = {'shape': shape, 'color': color}
    determine_power_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await send_clients_log_message(f"{color} placed a {color}_{shape} on {tile_to_place_on.name}")
    if old_shape:
        await send_clients_log_message(f"this trumped a {old_shape['color']}_{old_shape['shape']}")
    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_place", placer=color, shape=shape, index_of_tile_placed_at=tile_index, slot_index_placed_at=slot_index)

async def place_leader_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, color):
    game_state['location_of_leaders'][color] = tile_index
    determine_power_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await send_clients_log_message(f"{color} placed their leader on {game_state['tiles'][tile_index].name}")

async def player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, tile, shape_type):
    if None not in tile.slots_for_shapes:
        await send_clients_log_message(f"{player_color} cannot receive a {shape_type} on {tile.name}, no empty slots")
        return
    
    tile_index = find_index_of_tile_by_name(game_state, tile.name)
    next_empty_slot = tile.slots_for_shapes.index(None)
    tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
    await send_clients_log_message(f"{player_color} receives a {player_color}_{shape_type} on {tile.name}")
    determine_power_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_receive", receiver=player_color, shape=shape_type, index_of_tile_received_at=tile_index, index_of_slot_received_at=next_empty_slot)

async def move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, from_tile_index, from_slot_index, to_tile_index, to_slot_index):
    shape_to_move = game_state["tiles"][from_tile_index].slots_for_shapes[from_slot_index]
    
    if shape_to_move is None:
        return False

    if game_state["tiles"][to_tile_index].slots_for_shapes[to_slot_index] is not None:
        return False

    game_state["tiles"][from_tile_index].slots_for_shapes[from_slot_index] = None
    game_state["tiles"][to_tile_index].slots_for_shapes[to_slot_index] = shape_to_move

    await send_clients_log_message(f"moved a {shape_to_move['color']}_{shape_to_move['shape']} from {game_state['tiles'][from_tile_index].name} to {game_state['tiles'][to_tile_index].name}")
    determine_power_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_move", shape=shape_to_move["shape"], from_tile_index=from_tile_index, to_tile_index=to_tile_index)

    return True

async def burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, slot_index):
    tile = game_state["tiles"][tile_index]
    shape = tile.slots_for_shapes[slot_index]["shape"]
    color = tile.slots_for_shapes[slot_index]["color"]
    tile.slots_for_shapes[slot_index] = None
    await send_clients_log_message(f"burning a {color}_{shape} at {tile.name}")
    determine_power_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_burn", burner=game_action_container_stack[-1].whose_action, shape=shape, color=color, index_of_tile_burned_at=tile_index)


async def call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, event_type, **data):
    reactions_by_player = {"red":   game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="choose_a_reaction_to_resolve",
                                    required_data_for_action={"tier_to_react_with": {}},
                                    tiers_to_resolve={},
                                    data_from_event=data,
                                    whose_action="red",
                                ),
                            "blue": game_action_container.GameActionContainer(
                                    event=asyncio.Event(),
                                    game_action="choose_a_reaction_to_resolve",
                                    required_data_for_action={"tier_to_react_with": {}},
                                    tiers_to_resolve={},
                                    data_from_event=data,
                                    whose_action="blue",
                            ) }


    for _, listener_function in game_state["listeners"][event_type].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data)
        determine_power_levels(game_state)
        update_presence(game_state)
        determine_rulers(game_state)
        await send_clients_game_state(game_state)

    first_player = game_state['first_player']
    second_player = get_other_player_color(first_player)
    
    for player in [first_player, second_player]:
        if reactions_by_player[player].tiers_to_resolve:
            await send_clients_log_message(f"{player} must choose order to resolve reactions in")
            game_action_container_stack.append(reactions_by_player[player])
            await get_and_send_available_actions()
            await game_action_container_stack[-1].event.wait()

        #clean up reactions used by first player
        for tile_index, tier_indices in list(reactions_by_player[second_player].tiers_to_resolve.items()):
            tiers_to_remove = []
            for tier_index in tier_indices:
                if game_state['tiles'][tile_index].power_tiers[tier_index]['is_on_cooldown']:
                    tiers_to_remove.append(tier_index)
            
            for tier_index in tiers_to_remove:
                reactions_by_player[second_player].tiers_to_resolve[tile_index].remove(tier_index)
            
            if not reactions_by_player[second_player].tiers_to_resolve[tile_index]:
                del reactions_by_player[second_player].tiers_to_resolve[tile_index]
#sync
def has_presence(tile, color):
    """
    Check if a player has at least one shape on a given tile.
    
    :param tile: The tile to check
    :param color: The color of the player ("red" or "blue")
    :return: True if the player has at least one shape on the tile, False otherwise
    """
    return any(
        slot is not None and slot["color"] == color
        for slot in tile.slots_for_shapes
    )

def update_presence(game_state):
    """
    Update the presence for both players in the game state.
    
    :param game_state: The current game state
    """
    presence = {"red": 0, "blue": 0}

    for tile in game_state["tiles"]:
        for color in ["red", "blue"]:
            if has_presence(tile, color):
                presence[color] += 1

    # Update the game state with the calculated presence
    game_state["presence"] = presence

def count_all_shapes_for_color_on_tile(color, tile):
    return sum(1 for slot in tile.slots_for_shapes if slot and slot["color"] == color)

def get_available_client_actions(game_state, game_action_container, player_color_to_get_actions_for):
    if game_action_container.whose_action != player_color_to_get_actions_for:
        return {}
    
    available_client_actions = {}

    if game_action_container.game_action == 'place_shape_on_tile_slot':
        shape_type_to_place = game_action_container.required_data_for_action["shape_type_to_place"]
        slots_that_can_be_placed_on = get_tile_slots_that_can_be_placed_on(game_state, shape_type_to_place, game_action_container.whose_action)
        available_client_actions["select_a_slot_on_a_tile"] = slots_that_can_be_placed_on

    elif game_action_container.game_action == 'initial_circle_placement':
        slots_that_can_be_placed_on = get_tile_slots_that_can_be_placed_on(game_state, 'circle', game_action_container.whose_action)
        available_client_actions["select_a_slot_on_a_tile"] = slots_that_can_be_placed_on

    elif game_action_container.game_action == 'initial_leader_placement':
        slots_that_can_be_placed_on = get_tile_slots_that_can_be_placed_on(game_state, 'circle', game_action_container.whose_action)
        available_client_actions["select_a_tile"] = game_constants.all_tile_indices

    elif game_action_container.game_action == 'use_a_tier':
        index_of_tile_in_use = game_action_container.required_data_for_action["index_of_tile_in_use"]
        index_of_tier_in_use = game_action_container.required_data_for_action["index_of_tier_in_use"]
        tile_in_use = game_state["tiles"][index_of_tile_in_use]
        tile_in_use.set_available_actions_for_use(game_state, index_of_tier_in_use, game_action_container, available_client_actions)

    elif game_action_container.game_action == 'choose_a_reaction_to_resolve':
        available_client_actions['select_a_tier'] = game_action_container.tiers_to_resolve
    #must be an initial_decision
    else:
        available_client_actions['select_a_tier'] = {}
        available_client_actions['pass'] = []

        for tile_index, tile in enumerate(game_state["tiles"]):
            available_client_actions['select_a_tier'][tile_index] = tile.get_useable_tiers(game_state)

    return available_client_actions

def get_other_player_color(player_color):
    return 'blue' if player_color == 'red' else 'red'

def determine_rulers(game_state):
    for tile in game_state["tiles"]:
        tile.determine_ruler(game_state)

def determine_power_levels(game_state):
    game_state['peak_power']['red'] = 0
    game_state['peak_power']['blue'] = 0
    for tile in game_state["tiles"]:
        tile.determine_power()
        game_state['peak_power']['red'] = max(tile.power_per_player['red'], game_state['peak_power']['red'])
        game_state['peak_power']['blue'] = max(tile.power_per_player['blue'], game_state['peak_power']['blue'])

def set_peak_power(game_state):
    """
    Determine and set the peak power for both players in the game state.
    Peak power is the highest power a player has on any single tile.

    :param game_state: The current game state
    """
    peak_power = {
        "red": 0,
        "blue": 0
    }

    for tile in game_state["tiles"]:
        # Ensure the tile's power is up to date
        tile.determine_power()

        # Update peak power for red player
        if tile.red_power > peak_power["red"]:
            peak_power["red"] = tile.red_power

        # Update peak power for blue player
        if tile.blue_power > peak_power["blue"]:
            peak_power["blue"] = tile.blue_power

    # Set the calculated peak power in the game state
    game_state["peak_power"] = peak_power

def count_sets_on_tile_for_color(tile, color,):
    shape_counts = {"circle": 0, "square": 0, "triangle": 0}
    for slot in tile.slots_for_shapes:
        if slot and slot["color"] == color:
            shape_counts[slot["shape"]] += 1
    return min(shape_counts.values())

def get_tile_indices_where_player_has_presence(game_state, player):
    """
    Return a list of tile indices where the specified player has presence.

    :param game_state: The current game state
    :param player: The player color ('red' or 'blue')
    :return: A list of tile indices where the player has presence
    """
    tile_indices = []

    for index, tile in enumerate(game_state["tiles"]):
        if has_presence(tile, player):
            tile_indices.append(index)

    return tile_indices

def find_index_of_tile_by_name(game_state, name):
    for index, tile in enumerate(game_state["tiles"]):
        if tile.name == name:
            return index
    return None

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

def find_max_unique_pairs(remaining_shapes, current_pairs):
    if len(remaining_shapes) < 2:
        return len(current_pairs)
    
    max_pairs = len(current_pairs)
    
    for i in range(len(remaining_shapes) - 1):
        for j in range(i + 1, len(remaining_shapes)):
            shape1, shape2 = remaining_shapes[i], remaining_shapes[j]
            new_pair = tuple(sorted([shape1, shape2]))
            
            if new_pair not in current_pairs:
                # Make a new pair
                new_remaining = remaining_shapes[:i] + remaining_shapes[i+1:j] + remaining_shapes[j+1:]
                new_current_pairs = current_pairs | {new_pair}
                
                # Recursive call
                pairs_count = find_max_unique_pairs(new_remaining, new_current_pairs)
                max_pairs = max(max_pairs, pairs_count)
    
        return max_pairs

#returns a dict where the keys are tile indices and the associated list are the indices of the slots on that tile that can be placed on
def get_tile_slots_that_can_be_placed_on(game_state, shape_type, color):
    
    tile_slots_that_can_be_placed_on = {}

    for tile_index, tile in enumerate(game_state["tiles"]):
        slots_for_tile = []
        if shape_type in tile.shapes_which_can_be_placed_on_this:
            for slot_index, slot in enumerate(tile.slots_for_shapes):
                if slot is None or (game_constants.shape_power[slot['shape']] < game_constants.shape_power[shape_type] and color == slot['color']):
                    slots_for_tile.append(slot_index)
            if slots_for_tile:
                tile_slots_that_can_be_placed_on[tile_index] = slots_for_tile
    
    return tile_slots_that_can_be_placed_on

def get_slots_with_a_shape_of_player_color_at_tile_index(game_state, player_color, tile_index):
    slots_with_shape = []
    tile = game_state["tiles"][tile_index]
    
    for slot_index, slot in enumerate(tile.slots_for_shapes):
        if slot and slot["color"] == player_color:
            slots_with_shape.append(slot_index)
    
    return slots_with_shape

def determine_if_directly_adjacent(index1, index2):
    return index1 in get_adjacent_tile_indices(index2)

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

def find_longest_chain_of_ruled_tiles(tiles):
    def dfs(index, color, visited):
        if index in visited or tiles[index].ruler != color:
            return 0
        
        visited.add(index)
        max_length = 1
        
        for adjacent in get_adjacent_tile_indices(index):
            max_length = max(max_length, 1 + dfs(adjacent, color, visited))
        
        return max_length

    red_max = 0
    blue_max = 0
    
    for i in range(9):
        if tiles[i].ruler == "red":
            red_max = max(red_max, dfs(i, "red", set()))
        elif tiles[i].ruler == "blue":
            blue_max = max(blue_max, dfs(i, "blue", set()))

    return {"red": red_max, "blue": blue_max}