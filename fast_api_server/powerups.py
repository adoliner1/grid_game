import game_utilities

class Powerup:
    def __init__(self, name, description, number_of_slots, owner, listener_type=None, data_needed_for_use=[], is_on_cooldown=False):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.owner = owner
        self.listener_type = listener_type
        self.data_needed_for_use = data_needed_for_use
        self.is_on_cooldown=is_on_cooldown

    def is_useable(self, game_state):
        return False

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "slots_for_shapes": self.slots_for_shapes,
            "is_on_cooldown": self.is_on_cooldown
        } 
    
    def set_available_actions_for_use(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
    def set_available_client_actions_for_reaction(game_state, current_action, current_piece_of_data_to_fill_in_current_action, available_actions_with_details):
        return available_actions_with_details
    
class ProduceCirclesFor4Circles(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Produce 2 Circles For 4 Circles",
            description = "If filled with circles, produce 2 circles at the start of the round",
            number_of_slots=4,
            owner=owner
        )

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot["shape"] == "circle":
                    circle_count += 1
        if circle_count == 4:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 2, "circle", self.name)


class ProduceCircleFor3Shapes(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Produce Circle For 3 Shapes",
            description = "If filled, produce 1 circle at the start of the round",
            number_of_slots=3,
            owner=owner
        )

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot:
                    count += 1
        if count == 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, "circle", self.name)


class BurnTwoCirclesProduceTriangle(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Burn Two Circles Produce Triangle",
            description = "If filled with circles, you may burn 2 circles here to produce a triangle",
            number_of_slots=5,
            owner=owner
        )

    def is_useable(self, game_state):
        circle_count = 0
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "circle":
                circle_count += 1

        return circle_count == 5
    
    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):    
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Not enough circles on {self.name} to use it")
            return False
        
        await game_utilities.burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, game_utilities.find_index_of_powerup_by_name(game_state, self.name), self.number_of_slots-1)
        await game_utilities.burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, game_utilities.find_index_of_powerup_by_name(game_state, self.name), self.number_of_slots-2)
        await send_clients_log_message(f"{self.name} is used")
        
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, 'triangle', self.name)
        return True

class ProduceTriangleFor3Squares(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Produce Triangle For 3 Squares",
            description = "If filled with squares, produce 1 triangle at the start of the round",
            number_of_slots=3,
            owner=owner
        )

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        square_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                if slot["shape"] == "square":
                    square_count += 1
        if square_count == 3:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, "square", self.name)

class BurnFor3Or2Circles(Powerup):
    def __init__(self, owner):
        super().__init__(
            name = "Burn For 3 or 1 Circles",
            description = "Burn all your shapes here. If you burned at least 2, produce 1 circle. If you burned 5, produce 2 more and gain 2 points",
            number_of_slots=5,
            owner=owner
        )

    def is_useable(self, game_state):
        shape_count = 0
        for slot in self.slots_for_shapes:
            if slot:
                shape_count += 1
        return shape_count > 0
    
    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):    
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Need at least one shape on {self.name} to use it")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        shapes_burned = 0
        for index, slot in enumerate(self.slots_for_shapes):
            if slot:
                shapes_burned += 1
                await game_utilities.burn_shape_at_powerup_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, game_utilities.find_index_of_powerup_by_name(game_state, self.name), index)
        
        if shapes_burned == 5:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 3, 'circle', self.name)
            await send_clients_log_message(f"{self.owner} gains 2 points from {self.name}")
            game_state["points"][self.owner] += 2
        elif shapes_burned >= 2:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, self.owner, 1, 'circle', self.name)
        return True

class BurnForPoints(Powerup):
    def __init__(self, owner):
        super().__init__(
            name="Burn for Points",
            description="When filled, once per round, you may use this to burn one your shapes on a tile. If you did, +2 points",
            number_of_slots=3,
            owner=owner,
            data_needed_for_use=["slot_and_tile_to_burn_shape_from"]
        )

    def is_useable(self, game_state):
        return len([slot for slot in self.slots_for_shapes if slot]) == 3 and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill == "slot_and_tile_to_burn_shape_from":
            slots_with_a_burnable_shape = {}
            for tile_index, tile in enumerate(game_state["tiles"]):
                slots_with_shapes = []
                for slot_index, slot in enumerate(tile.slots_for_shapes):
                    if slot and slot["color"] == self.owner:
                        slots_with_shapes.append(slot_index)
                if slots_with_shapes:
                    slots_with_a_burnable_shape[tile_index] = slots_with_shapes
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Cannot use {self.name} it's on cooldown or doesn't have enough shapes")
            return False

        slot_and_tile_to_burn_shape_from = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape_from']
        tile_index = slot_and_tile_to_burn_shape_from['tile_index']
        slot_index = slot_and_tile_to_burn_shape_from['slot_index']
        tile = game_state["tiles"][tile_index]
        if not tile.slots_for_shapes[slot_index] or tile.slots_for_shapes[slot_index]["color"] != self.owner:
            await send_clients_log_message(f"Cannot burn shape that doesn't belong to {self.owner}")
            return False

        await send_clients_log_message(f"Using {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, tile_index, slot_index)
        game_state["points"][self.owner] += 2
        await send_clients_log_message(f"{self.owner} gains 2 points from using {self.name}")
        self.is_on_cooldown = True
        return True
    

class SwapPositionOfTileWithAdjacentTile(Powerup):
    def __init__(self, owner):
        super().__init__(
            name="Swap Position Of Tile With Adjacent Tile",
            description="When filled with squares, once per round, you may use this to swap the position of a tile with an adjacent tile",
            number_of_slots=3,
            owner=owner,
            data_needed_for_use=["first_tile", "adjacent_tile_to_first_tile"]
        )

    def is_useable(self, game_state):
        return len([slot["shape"] == "square" for slot in self.slots_for_shapes if slot]) == 3 and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()

        if current_piece_of_data_to_fill == "first_tile":
            available_actions["select_a_tile"] = list(range(len(game_state["tiles"])))
        else:
            game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["first_tile"])
            available_actions["select_a_tile"] = game_utilities.get_adjacent_tile_indices(game_action_container.required_data_for_action["first_tile"])

    async def use_powerup(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]

        if not self.is_useable:
            await send_clients_log_message(f"Tried to use {self.name} but don't have the squares or it's on cooldown")   

        tile1_index = game_action_container.required_data_for_action['first_tile']
        tile2_index = game_action_container.required_data_for_action['adjacent_tile_to_first_tile']

        if tile1_index is None or tile2_index is None:
            await send_clients_log_message(f"Invalid tiles selected while using {self.name}")
            return False

        if tile1_index not in game_utilities.get_adjacent_tile_indices(tile2_index):
            await send_clients_log_message(f"Chose non-adjacent tiles while using {self.name}")
            return False            

        if tile1_index == tile2_index:
            await send_clients_log_message(f"Cannot select the same tile twice for {self.name}")
            return False

        await send_clients_log_message(f"Using {self.name} to swap tiles at indices {tile1_index} and {tile2_index}")

        # Swap the tiles
        game_state["tiles"][tile1_index], game_state["tiles"][tile2_index] = game_state["tiles"][tile2_index], game_state["tiles"][tile1_index]
        self.is_on_cooldown = True
        return True