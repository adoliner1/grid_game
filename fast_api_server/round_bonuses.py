class RoundBonus:
    def __init__(self, name, description, listener_type):
        self.name = name
        self.description = description
        self.listener_type = listener_type

    def setup(self, game_state):
        game_state["listeners"][self.listener_type][self.name] = self.run_effect

    def cleanup(self, game_state):
        del game_state["listeners"][self.listener_type][self.name]

    def serialize(self):
        return self.description

class PointsPerCircle(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Circle",
            description = "Gain 1 point when you place a circle",
            listener_type="on_place",
        )

    async def run_effect(self, game_state, callback, **data):
        placer = data.get('placer')
        shape = data.get('shape')

        if (shape == "circle"):
            game_state["points"][placer] += 1
            await callback(f"{placer} gets 1 point for placing a circle (round bonus)")