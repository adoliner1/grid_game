import asyncio
import game_action_container
import game_constants

#async
async def produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player_color, amount, shape_type, calling_entity_name):

    game_state["shapes_in_storage"][player_color][shape_type] += amount

    if calling_entity_name:
        await send_clients_log_message(f" {calling_entity_name} produced {amount} {shape_type}(s) for {player_color}")
    else:
        await send_clients_log_message(f" {player_color} produced {amount} {shape_type}(s)")

    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    for _, listener_function in game_state["listeners"]["on_produce"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, amount_produced=amount, producer=player_color, shape=shape_type, producing_tile_name=calling_entity_name)
        
async def place_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, tile_index, slot_index, shape, color):
    tile_to_place_on = game_state["tiles"][tile_index]
    old_shape = tile_to_place_on.slots_for_shapes[slot_index]  
    tile_to_place_on.slots_for_shapes[slot_index] = {'shape': shape, 'color': color}
    await send_clients_log_message(f"{color} placed a {shape} on {tile_to_place_on.name}")
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    #add a reaction to the stack so that the owner can place it on a powerup, send out available actions to the clients, then wait for the reaction to resolve
    if old_shape:
        new_container = game_action_container.GameActionContainer(
                        event=asyncio.Event(),
                        game_action="place_shape_on_powerup_slot",
                        required_data_for_action={"resettable_powerup_slot_to_place_on": {}, "shape_type_to_place": old_shape["shape"]},
                        whose_action=old_shape["color"],
                        is_a_reaction=True,
                    )
        #if no available actions, don't add reaction
        if not get_available_client_actions(game_state, new_container, old_shape["color"]) == {}:
            game_action_container_stack.append(new_container)
            await send_clients_available_actions(get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
            await send_clients_available_actions(get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
            await game_action_container_stack[-1].event.wait()

    for _, listener_function in game_state["listeners"]["on_place"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, placer=color, shape=shape, index_of_tile_placed_at=tile_index)  

async def place_shape_on_powerup(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, powerup_index, slot_index, shape, color):
    game_state["powerups"][color][powerup_index].slots_for_shapes[slot_index] = {'shape': shape, 'color': color}   

    await send_clients_log_message(f"{color} placed a {shape} on {game_state['powerups'][color][powerup_index].name}")
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
 
    for _, listener_function in game_state["listeners"]["on_powerup_place"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, placer=color, shape=shape, index_of_powerup_placed_at=powerup_index)

async def player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player_color, tile, shape_type):
    if None not in tile.slots_for_shapes:
        await send_clients_log_message(f"{player_color} cannot receive a {shape_type} on {tile.name}, no empty slots")
        return
    
    tile_index = find_index_of_tile_by_name(game_state, tile.name)
    next_empty_slot = tile.slots_for_shapes.index(None)
    tile.slots_for_shapes[next_empty_slot] = {"shape": shape_type, "color": player_color}
    await send_clients_log_message(f"{player_color} receives a {shape_type} on {tile.name}")

    for _, listener_function in game_state["listeners"]["on_receive"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, receiver=player_color, shape=shape_type, index_of_tile_placed_at=tile_index)

    determine_rulers(game_state)

async def move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, from_tile_index, from_slot_index, to_tile_index, to_slot_index):
    shape_to_move = game_state["tiles"][from_tile_index].slots_for_shapes[from_slot_index]
    
    if shape_to_move is None:
        return False

    if game_state["tiles"][to_tile_index].slots_for_shapes[to_slot_index] is not None:
        return False

    game_state["tiles"][from_tile_index].slots_for_shapes[from_slot_index] = None
    game_state["tiles"][to_tile_index].slots_for_shapes[to_slot_index] = shape_to_move

    await send_clients_log_message(f"moved a {shape_to_move['color']} {shape_to_move['shape']} from {game_state['tiles'][from_tile_index].name} to {game_state['tiles'][to_tile_index].name}")
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    for _, listener_function in game_state["listeners"]["on_move"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, shape=shape_to_move["shape"], from_tile_index=from_tile_index, to_tile_index=to_tile_index)

    return True

async def burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, tile_index, slot_index):
    tile = game_state["tiles"][tile_index]
    shape = tile.slots_for_shapes[slot_index]["shape"]
    color = tile.slots_for_shapes[slot_index]["color"]
    tile.slots_for_shapes[slot_index] = None
    await send_clients_log_message(f"burning a {color} {shape} at {tile.name}")
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    for _, listener_function in game_state["listeners"]["on_burn"].items():
        await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, burner=game_action_container_stack[-1].whose_action, shape=shape, index_of_tile_burned_at=tile_index)

async def burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, powerup_color, powerup_index, slot_index):
    powerup = game_state["powerups"][powerup_color][powerup_index]
    shape = powerup.slots_for_shapes[slot_index]["shape"]
    color = powerup.slots_for_shapes[slot_index]["color"]
    powerup.slots_for_shapes[slot_index] = None
    await send_clients_log_message(f"burning a {color} {shape} at {powerup.name}")
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    #for _, listener_function in game_state["listeners"]["on_burn"].items():
    #    await listener_function(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, burner=game_action_container_stack[-1].whose_action, shape=shape, index_of_tile_burned_at=powerup_index)

#sync
def get_available_client_actions(game_state, game_action_container, player_color_to_get_actions_for):

    if game_action_container.whose_action != player_color_to_get_actions_for:
        return {}
    
    available_client_actions = {}

    if game_action_container.game_action == 'place_shape_on_tile_slot':
        shape_type_to_place = game_action_container.required_data_for_action["shape_type_to_place"]
        slots_that_can_be_placed_on = get_tile_slots_that_can_be_placed_on(game_state, shape_type_to_place)
        available_client_actions["select_a_slot_on_a_tile"] = slots_that_can_be_placed_on

    elif game_action_container.game_action == 'place_shape_on_powerup_slot':
        shape_type_to_place = game_action_container.required_data_for_action["shape_type_to_place"]
        slots_that_can_be_placed_on = get_powerup_slots_that_can_be_placed_on(game_state, game_action_container.whose_action, shape_type_to_place)
        available_client_actions["select_a_slot_on_a_powerup"] = slots_that_can_be_placed_on

    elif game_action_container.game_action == 'use_tile':
        index_of_tile_in_use = game_action_container.required_data_for_action["index_of_tile_in_use"]
        tile_in_use = game_state["tiles"][index_of_tile_in_use]
        tile_in_use.set_available_actions_for_use(game_state, game_action_container, available_client_actions)

    elif game_action_container.game_action == "use_powerup":
        index_of_powerup_in_use = game_action_container.required_data_for_action["index_of_powerup_in_use"]
        powerup_in_use = game_state["powerups"][game_state.whose_turn_is_it][index_of_powerup_in_use]
        powerup_in_use.set_available_actions_for_use(game_state, game_action_container, available_client_actions)        

    elif game_action_container.game_action == 'react_with_tile':
        index_of_tile_being_reacted_with = game_action_container.required_data_for_action["index_of_tile_being_reacted_with"]
        tile_being_reacted_with = game_state["tiles"][index_of_tile_being_reacted_with]
        tile_being_reacted_with.set_available_actions_for_reaction(game_state, game_action_container, available_client_actions)

    elif game_action_container.game_action == "react_with_powerup":
        index_of_powerup_being_reacted_with = game_action_container.required_data_for_action["index_of_powerup_being_reacted_with"]
        powerup_being_reacted_with = game_state["powerups"][game_state.whose_turn_is_it][index_of_powerup_being_reacted_with]
        powerup_being_reacted_with.set_available_actions_for_reaction(game_state, game_action_container, available_client_actions)

    #must be an initial_decision
    else:
        available_client_actions['select_a_shape_in_storage'] = []
        available_client_actions['select_a_tile'] = []
        available_client_actions['select_a_powerup'] = []
        available_client_actions['pass'] = []

        for shape, amount in game_state["shapes_in_storage"][game_action_container.whose_action].items():
            if amount > 0:
                available_client_actions["select_a_shape_in_storage"].append(shape)

        for tile_index, tile in enumerate(game_state["tiles"]):
            if tile.is_useable(game_state):
                available_client_actions['select_a_tile'].append(tile_index)
    
        for powerup_index, powerup in enumerate(game_state["powerups"][game_action_container.whose_action]):
            if powerup.is_useable(game_state):
                available_client_actions['select_a_powerup'].append(powerup_index)

    return available_client_actions

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

def find_index_of_powerup_by_name(game_state, name):
    for index, powerup in enumerate(game_state["powerups"]["red"]):
        if powerup.name == name:
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

#returns a dict where the keys are tile indices and the associated list are the indices of the slots on that tile that can be placed on
def get_tile_slots_that_can_be_placed_on(game_state, shape_type):
    
    shape_strength = game_constants.shape_hierarchy.get(shape_type)
    tile_slots_that_can_be_placed_on = {}

    for tile_index, tile in enumerate(game_state["tiles"]):
        slots_for_tile = []
        for slot_index, slot in enumerate(tile.slots_for_shapes):
            if slot is None or game_constants.shape_hierarchy.get(slot["shape"]) < shape_strength:
                slots_for_tile.append(slot_index)
        if slots_for_tile:
            tile_slots_that_can_be_placed_on[tile_index] = slots_for_tile
    
    return tile_slots_that_can_be_placed_on

def get_powerup_slots_that_can_be_placed_on(game_state, player_color, shape_type):
    shape_strength = game_constants.shape_hierarchy.get(shape_type)
    powerup_slots_that_can_be_placed_on = {"red": {}, "blue": {}}
    
    for color in game_constants.player_colors:
        if player_color == color:
            for powerup_index, powerup in enumerate(game_state["powerups"][color]):
                slots_for_powerup = []
                for slot_index, slot in enumerate(powerup.slots_for_shapes):
                    if slot is None or game_constants.shape_hierarchy.get(slot["shape"]) < shape_strength:
                        slots_for_powerup.append(slot_index)
                if slots_for_powerup:
                    powerup_slots_that_can_be_placed_on[color][powerup_index] = slots_for_powerup
   
    return powerup_slots_that_can_be_placed_on

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