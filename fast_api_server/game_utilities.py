import asyncio
import game_action_container
import game_constants

async def recruit_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, slot_index, disciple, color):
    tile_to_recruit_on = game_state["tiles"][tile_index]
    old_disciple =  tile_to_recruit_on.slots_for_disciples[slot_index]
    tile_to_recruit_on.slots_for_disciples[slot_index] = {'disciple': disciple, 'color': color}
    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await send_clients_log_message(f"{color} recruited a {color}_{disciple} at **{tile_to_recruit_on.name}**")
    if old_disciple:
        await send_clients_log_message(f"this replaced a {old_disciple['color']}_{old_disciple['disciple']}")
    await call_listener_functions_for_event_type(game_state,
                                                  game_action_container_stack,
                                                    send_clients_log_message,
                                                      get_and_send_available_actions,
                                                        send_clients_game_state,
                                                          "on_recruit",
                                                            recruiter=color,
                                                              disciple=disciple,
                                                                index_of_tile_recruited_at=tile_index,
                                                                  slot_index_recruited_at=slot_index)
    
async def exile_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, slot_index_to_exile_from, color_of_player_exiling):
    tile_to_exile_from = game_state["tiles"][tile_index]
    old_disciple =  tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from]
    tile_to_exile_from.slots_for_disciples[slot_index_to_exile_from] = None

    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    await send_clients_log_message(f"{color_of_player_exiling} exiled a {old_disciple['color']}_{old_disciple['disciple']} from **{tile_to_exile_from.name}** for {game_state['costs_to_exile'][color_of_player_exiling][old_disciple['disciple']]} power")

    await call_listener_functions_for_event_type(game_state,
                                                  game_action_container_stack,
                                                    send_clients_log_message,
                                                      get_and_send_available_actions,
                                                        send_clients_game_state,
                                                          "on_exile",
                                                            exiler=color_of_player_exiling,
                                                              disciple=old_disciple,
                                                                index_of_tile_exiled_at=tile_index,
                                                                  slot_index_exiled_at=slot_index_to_exile_from)

async def place_leader_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, color):
    game_state['tiles'][tile_index].leaders_here[color] = True
    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await send_clients_log_message(f"{color}_leader starts on **{game_state['tiles'][tile_index].name}**")

async def player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, tile, disciple_type):
    if None not in tile.slots_for_disciples:
        await send_clients_log_message(f"{player_color} cannot receive a {disciple_type} on **{tile.name}**, no empty slots")
        return
    
    tile_index = find_index_of_tile_by_name(game_state, tile.name)
    next_empty_slot = tile.slots_for_disciples.index(None)
    tile.slots_for_disciples[next_empty_slot] = {"disciple": disciple_type, "color": player_color}
    await send_clients_log_message(f"{player_color} receives a {player_color}_{disciple_type} on **{tile.name}**")
    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_receive", receiver=player_color, disciple=disciple_type, index_of_tile_received_at=tile_index, index_of_slot_received_at=next_empty_slot)

async def move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, from_tile_index, from_slot_index, to_tile_index, to_slot_index):
    disciple_to_move = game_state["tiles"][from_tile_index].slots_for_disciples[from_slot_index]
    
    if disciple_to_move is None:
        return False

    if game_state["tiles"][to_tile_index].slots_for_disciples[to_slot_index] is not None:
        return False

    game_state["tiles"][from_tile_index].slots_for_disciples[from_slot_index] = None
    game_state["tiles"][to_tile_index].slots_for_disciples[to_slot_index] = disciple_to_move

    await send_clients_log_message(f"moved a {disciple_to_move['color']}_{disciple_to_move['disciple']} from **{game_state['tiles'][from_tile_index].name}** to **{game_state['tiles'][to_tile_index].name}**")
    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)
    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_move", disciple=disciple_to_move["disciple"], from_tile_index=from_tile_index, to_tile_index=to_tile_index)

    return True

async def burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index, slot_index):
    tile = game_state["tiles"][tile_index]
    disciple = tile.slots_for_disciples[slot_index]["disciple"]
    color = tile.slots_for_disciples[slot_index]["color"]
    tile.slots_for_disciples[slot_index] = None
    await send_clients_log_message(f"burning a {color}_{disciple} at **{tile.name}**")
    determine_influence_levels(game_state)
    update_presence(game_state)
    determine_rulers(game_state)
    await send_clients_game_state(game_state)

    await call_listener_functions_for_event_type(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, "on_burn", burner=game_action_container_stack[-1].whose_action, disciple=disciple, color=color, index_of_tile_burned_at=tile_index)


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
        determine_influence_levels(game_state)
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
                if game_state['tiles'][tile_index].influence_tiers[tier_index]['is_on_cooldown']:
                    tiers_to_remove.append(tier_index)
            
            for tier_index in tiers_to_remove:
                reactions_by_player[second_player].tiers_to_resolve[tile_index].remove(tier_index)
            
            if not reactions_by_player[second_player].tiers_to_resolve[tile_index]:
                del reactions_by_player[second_player].tiers_to_resolve[tile_index]
#sync
def get_tile_index_of_leader(game_state, color):
    for tile_index, tile in enumerate(game_state['tiles']):
        if tile.leaders_here[color]:
            return tile_index

def has_presence(tile, color):
    """
    Check if a player has at least one disciple or a leader on a given tile.
   
    :param tile: The tile to check
    :param color: The color of the player ("red" or "blue")
    :return: True if the player has at least one disciple or a leader on the tile, False otherwise
    """
    return (
        any(slot is not None and slot["color"] == color for slot in tile.slots_for_disciples)
        or tile.leaders_here[color]
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

def count_all_disciples_for_color_on_tile(color, tile):
    return sum(1 for slot in tile.slots_for_disciples if slot and slot["color"] == color)

def get_available_client_actions(game_state, game_action_container, player_color_to_get_actions_for):
    if game_action_container.whose_action != player_color_to_get_actions_for:
        return {}
    
    available_client_actions = {}

    if game_action_container.game_action == 'initial_follower_placement':
        slots_that_can_be_placed_on = get_tile_slots_that_can_be_placed_on(game_state, 'follower', game_action_container.whose_action)
        available_client_actions["select_a_slot_on_a_tile"] = slots_that_can_be_placed_on

    elif game_action_container.game_action == 'initial_leader_placement':
        available_client_actions["select_a_tile"] = game_constants.all_tile_indices

    elif game_action_container.game_action == 'use_a_tier':
        index_of_tile_in_use = game_action_container.required_data_for_action["index_of_tile_in_use"]
        index_of_tier_in_use = game_action_container.required_data_for_action["index_of_tier_in_use"]
        tile_in_use = game_state["tiles"][index_of_tile_in_use]
        tile_in_use.set_available_actions_for_use(game_state, index_of_tier_in_use, game_action_container, available_client_actions)

    elif game_action_container.game_action == 'move_leader':
        #after the first move, players can choose to stop their movement
        if game_action_container.movements_made > 0:
            available_client_actions["do_not_react"] = None
        available_client_actions["select_a_tile"] = get_adjacent_tile_indices(get_tile_index_of_leader(game_state, game_action_container.whose_action))

    elif game_action_container.game_action == 'recruit':
        if game_action_container.get_next_piece_of_data_to_fill() == 'disciple_type_to_recruit':
            available_client_actions['select_a_disciple_in_the_HUD'] = get_disciples_that_can_be_recruited(game_state, game_action_container.whose_action)
        else:
            disciple_to_recruit = game_action_container.required_data_for_action['disciple_type_to_recruit']
            tiles_within_recruiting_range = get_tiles_within_recruiting_range(game_state, disciple_to_recruit, game_action_container.whose_action)
            available_client_actions['select_a_slot_on_a_tile'] = get_tile_slots_that_can_be_recruited_on(game_state, disciple_to_recruit, game_action_container.whose_action, tiles_within_recruiting_range)

    elif game_action_container.game_action == 'exile':
        tiles_within_exiling_range = get_tiles_within_exiling_range(game_state, game_action_container.whose_action)
        available_client_actions['select_a_slot_on_a_tile'] = get_tile_slots_that_can_be_exiled(game_state, game_action_container.whose_action, tiles_within_exiling_range)


    elif game_action_container.game_action == 'choose_a_reaction_to_resolve':
        available_client_actions['select_a_tier'] = game_action_container.tiers_to_resolve

    #giving actions for the initial_decision
    else:
        available_client_actions['pass'] = []

        if game_state['power'][game_action_container.whose_action] > 0:
            available_client_actions['move_leader'] = []
        if game_state['power'][game_action_container.whose_action] > 1:    
            available_client_actions['recruit'] = []
        if game_state['power'][game_action_container.whose_action] > 2:    
            available_client_actions['exile'] = []

        available_client_actions['select_a_tier'] = {}
        for tile_index, tile in enumerate(game_state["tiles"]):
            available_client_actions['select_a_tier'][tile_index] = tile.get_useable_tiers(game_state)

    return available_client_actions

def calculate_exiling_ranges(game_state):
    game_state['exiling_range']['red'] = game_constants.initial_exiling_ranges['red']
    game_state['exiling_range']['blue'] = game_constants.initial_exiling_ranges['blue']
    for tile in game_state['tiles']:
        tile.modify_exiling_ranges(game_state)

def calculate_exiling_costs(game_state):
    pass

def get_tiles_within_exiling_range(game_state, player_color):
    calculate_exiling_ranges(game_state)
    exiling_range = game_state['exiling_range'][player_color]
    location_of_leader = get_tile_index_of_leader(game_state, player_color)
    tiles_in_range = []

    leader_row = location_of_leader // game_constants.grid_size
    leader_col = location_of_leader % game_constants.grid_size

    for row in range(game_constants.grid_size):
        for col in range(game_constants.grid_size):
            distance = abs(row - leader_row) + abs(col - leader_col) 
            if distance <= exiling_range:
                tile_index = row * game_constants.grid_size + col
                tiles_in_range.append(tile_index)
    
    return tiles_in_range

def calculate_expected_incomes(game_state):
    round = game_state['round']
    if round < 5:
        game_state['expected_power_incomes']['red'] = game_constants.power_given_at_end_of_round[round]
        game_state['expected_power_incomes']['blue'] = game_constants.power_given_at_end_of_round[round]
    else:
        game_state['expected_power_incomes']['red'] = 0
        game_state['expected_power_incomes']['blue'] = 0

    game_state['expected_points_incomes']['red'] = 0
    game_state['expected_points_incomes']['blue'] = 0
    
    game_state['income_bonuses'][round].modify_expected_incomes(game_state)
    game_state['scorer_bonuses'][round].modify_expected_incomes(game_state)

    for tile in game_state['tiles']:
        tile.modify_expected_incomes(game_state)

def calculate_recruiting_ranges(game_state):
    game_state['recruiting_range']['red'] = game_constants.initial_recruiting_ranges['red']
    game_state['recruiting_range']['blue'] = game_constants.initial_recruiting_ranges['blue']
    for tile in game_state['tiles']:
        tile.modify_recruiting_ranges(game_state)

def calculate_recruiting_costs(game_state):
    pass

def get_tiles_within_recruiting_range(game_state, disciple_to_recruit, player_color):
    calculate_recruiting_ranges(game_state)
    recruiting_range = game_state['recruiting_range'][player_color]
    location_of_leader = get_tile_index_of_leader(game_state, player_color)
    tiles_in_range = []

    leader_row = location_of_leader // game_constants.grid_size
    leader_col = location_of_leader % game_constants.grid_size

    for row in range(game_constants.grid_size):
        for col in range(game_constants.grid_size):
            distance = abs(row - leader_row) + abs(col - leader_col)
            
            if distance <= recruiting_range:
                tile_index = row * game_constants.grid_size + col
                tiles_in_range.append(tile_index)
    
    return tiles_in_range

def get_disciples_that_can_be_recruited(game_state, player_color):
    calculate_recruiting_costs(game_state)
    disciples_that_can_be_recruited = []
    for disciple in game_constants.disciples:
        if game_state['costs_to_recruit'][player_color][disciple] <= game_state['power'][player_color]:
            disciples_that_can_be_recruited.append(disciple)
    return disciples_that_can_be_recruited

def get_other_player_color(player_color):
    return 'blue' if player_color == 'red' else 'red'

def determine_rulers(game_state):
    for tile in game_state["tiles"]:
        tile.determine_ruler(game_state)

def determine_influence_levels(game_state):
    game_state['peak_influence']['red'] = 0
    game_state['peak_influence']['blue'] = 0
    for tile in game_state["tiles"]:
        tile.determine_influence()
        game_state['peak_influence']['red'] = max(tile.influence_per_player['red'], game_state['peak_influence']['red'])
        game_state['peak_influence']['blue'] = max(tile.influence_per_player['blue'], game_state['peak_influence']['blue'])

def set_peak_influence(game_state):
    """
    Determine and set the peak influence for both players in the game state.
    Peak influence is the highest influence a player has on any single tile.

    :param game_state: The current game state
    """
    peak_influence = {
        "red": 0,
        "blue": 0
    }

    for tile in game_state["tiles"]:
        # Ensure the tile's influence is up to date
        tile.determine_influence()

        # Update peak influence for red player
        if tile.red_influence > peak_influence["red"]:
            peak_influence["red"] = tile.red_influence

        # Update peak influence for blue player
        if tile.blue_influence > peak_influence["blue"]:
            peak_influence["blue"] = tile.blue_influence

    # Set the calculated peak influence in the game state
    game_state["peak_influence"] = peak_influence

def count_sets_on_tile_for_color(tile, color,):
    disciple_counts = {"follower": 0, "acolyte": 0, "sage": 0}
    for slot in tile.slots_for_disciples:
        if slot and slot["color"] == color:
            disciple_counts[slot["disciple"]] += 1
    return min(disciple_counts.values())

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

def count_number_of_disciple_for_player_on_tile(disciple, player, tile):
    count = 0
    for slot in tile.slots_for_disciples:
        if slot and slot["disciple"] == disciple and slot["color"] == player:
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

def find_max_unique_pairs(remaining_disciples, current_pairs):
    if len(remaining_disciples) < 2:
        return len(current_pairs)
    
    max_pairs = len(current_pairs)
    
    for i in range(len(remaining_disciples) - 1):
        for j in range(i + 1, len(remaining_disciples)):
            disciple1, disciple2 = remaining_disciples[i], remaining_disciples[j]
            new_pair = tuple(sorted([disciple1, disciple2]))
            
            if new_pair not in current_pairs:
                # Make a new pair
                new_remaining = remaining_disciples[:i] + remaining_disciples[i+1:j] + remaining_disciples[j+1:]
                new_current_pairs = current_pairs | {new_pair}
                
                # Recursive call
                pairs_count = find_max_unique_pairs(new_remaining, new_current_pairs)
                max_pairs = max(max_pairs, pairs_count)
    
        return max_pairs

def get_tile_slots_that_can_be_recruited_on(game_state, disciple_type, color, tile_indices):
    
    tile_slots_that_can_be_recruited_on = {}

    for tile_index in tile_indices:
        slots_for_tile = []
        tile = game_state['tiles'][tile_index]
        if disciple_type in tile.disciples_which_can_be_recruited_to_this:
            for slot_index, slot in enumerate(tile.slots_for_disciples):
                if slot is None or (game_constants.disciple_influence[slot['disciple']] < game_constants.disciple_influence[disciple_type] and color == slot['color']):
                    slots_for_tile.append(slot_index)
            if slots_for_tile:
                tile_slots_that_can_be_recruited_on[tile_index] = slots_for_tile
    
    return tile_slots_that_can_be_recruited_on

def get_tile_slots_that_can_be_exiled(game_state, color, tile_indices):
    
    calculate_exiling_costs(game_state)
    tile_slots_that_can_be_exiled = {}

    for tile_index in tile_indices:
        slots_for_tile = []
        tile = game_state['tiles'][tile_index]
        for slot_index, slot in enumerate(tile.slots_for_disciples):
            if slot is not None and game_state['costs_to_exile'][color][slot['disciple']] <= game_state['power'][color]:
                slots_for_tile.append(slot_index)
        if slots_for_tile:
            tile_slots_that_can_be_exiled[tile_index] = slots_for_tile
    
    return tile_slots_that_can_be_exiled

#returns a dict where the keys are tile indices and the associated list are the indices of the slots on that tile that can be placed on
def get_tile_slots_that_can_be_placed_on(game_state, disciple_type, color):
    
    tile_slots_that_can_be_placed_on = {}

    for tile_index, tile in enumerate(game_state["tiles"]):
        slots_for_tile = []
        if disciple_type in tile.disciples_which_can_be_recruited_to_this:
            for slot_index, slot in enumerate(tile.slots_for_disciples):
                if slot is None or (game_constants.disciple_influence[slot['disciple']] < game_constants.disciple_influence[disciple_type] and color == slot['color']):
                    slots_for_tile.append(slot_index)
            if slots_for_tile:
                tile_slots_that_can_be_placed_on[tile_index] = slots_for_tile
    
    return tile_slots_that_can_be_placed_on

def get_slots_with_a_disciple_of_player_color_at_tile_index(game_state, player_color, tile_index):
    slots_with_disciple = []
    tile = game_state["tiles"][tile_index]
    
    for slot_index, slot in enumerate(tile.slots_for_disciples):
        if slot and slot["color"] == player_color:
            slots_with_disciple.append(slot_index)
    
    return slots_with_disciple

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