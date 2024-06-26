class Tile:
    def __init__(self, name, description, number_of_slots, ruling_criteria, ruling_benefits):
        self.name = name
        self.description = description
        self.number_of_slots = number_of_slots
        self.slots_for_shapes = [None] * number_of_slots
        self.ruling_criteria = ruling_criteria
        self.ruling_benefits = ruling_benefits

    def determine_ruler(self):
        pass

    def start_of_round_effect(self):
        pass

    def end_of_round_effect(self):
        pass

    def end_of_game_effect(self):
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

class AlgebraTile(Tile):
    def __init__(self):
        super().__init__(
            name="algebra",
            description="",
            number_of_slots=3,
            ruling_criteria="most shapes",
            ruling_benefits="at the start of the round, collect 1 circle"
        )

    def apply_ruler_effects():
        pass

    def determine_ruler():
        pass

    def apply_ruling_benefits(self, player):
        player.collect_shape("circle", 1)