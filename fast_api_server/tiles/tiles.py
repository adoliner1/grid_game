from fast_api_server.game_utilities import produce_shape_for_player, player_receives_a_shape_on_tile

class Tile:
    def __init__(self, name, description, number_of_slots, ruling_criteria, ruling_benefits):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.ruling_criteria = ruling_criteria
        self.ruling_benefits = ruling_benefits

    def determine_ruler(self, game_state):
        pass

    async def start_of_round_effect(self, game_state, callback):
        pass

    async def end_of_round_effect(self, game_state, callback):
        await callback(f"end of round effect placeholder for {self.name}")

    def end_of_game_effect(self, game_state, callback):
        pass

    def get_ruling_benefits(self):
        return self.ruling_benefits

    def get_ruling_criteria(self):
        return self.ruling_criteria

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "ruling_criteria": self.get_ruling_criteria(),
            "ruling_benefits": self.get_ruling_benefits(),
            "slots_for_shapes": self.slots_for_shapes
        }

class Algebra(Tile):
    def __init__(self):
        super().__init__(
            name="algebra",
            description="",
            number_of_slots=3,
            ruling_criteria="most shapes",
            ruling_benefits="at the start of the round, collect 1 circle"
        )

    def apply_ruler_effects(game_state):
        pass

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
            return 'red'
        elif blue_count > red_count:
            return 'blue'
        return None

    def apply_ruling_benefits(self, player, game_state):
        pass

    async def start_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'circle', callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'circle', callback)

class Boron(Tile):
    def __init__(self):
        super().__init__(
            name="boron",
            description="at the end of the round, if you have a square here, receive a circle here",
            number_of_slots=11,
            ruling_criteria="7 or more circles",
            ruling_benefits="at end of the game: 2vp. at end of round: produce 1 triangle"
        )

    def apply_ruler_effects(game_state):
        pass

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "circle":
                    red_count += 1
                elif slot["color"] == "blue" and slot["shape"] == "circle":
                    blue_count += 1
        if red_count >= 7:
            return 'red'
        elif blue_count >= 7:
            return 'blue'
        return None

    def apply_ruling_benefits(self, player, game_state):
        pass

    async def start_of_round_effect(self, game_state, callback):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await produce_shape_for_player(game_state, 'red', 1, 'circle', callback)
        elif (ruler == 'blue'):
            await produce_shape_for_player(game_state, 'blue', 1, 'circle', callback)

    async def end_of_round_effect(self, game_state, callback):

        red_has_square = False
        blue_has_square = False
        
        for slot in self.slots_for_shapes:
                
            if slot:
                if slot["color"] == "red" and slot["shape"] == "square":
                    red_has_square = True
                elif slot["color"] == "blue" and slot["shape"] == "square":
                    blue_has_square = True

        if red_has_square and blue_has_square:
            await callback(f"both players have a square on {self.name}")
            first_player = game_state["first_player"]
            second_player = 'red' if first_player == 'blue' else 'blue'
            await player_receives_a_shape_on_tile(game_state, first_player, self, 'circle', callback)
            await player_receives_a_shape_on_tile(game_state, second_player, self, 'circle', callback)
        
        elif red_has_square:
            player_receives_a_shape_on_tile(game_state, 'red', self, 'circle', callback)
            await callback(f"red has a square on {self.name}")
        elif blue_has_square:
            await callback(f"blue has a square on {self.name}")
            player_receives_a_shape_on_tile(game_state, 'blue', self, 'circle', callback)
