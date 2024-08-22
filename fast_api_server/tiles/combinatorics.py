import game_utilities
import game_constants
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            type="Producer/Scorer",
            description="At the end of a round, for each same-shape pair you have here, produce 1 shape of that type\nPer set you have here, +3 points per shape you produced this way\nRuler: Most shapes",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        red_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_shapes = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
       
        if red_shapes > blue_shapes:
            self.ruler = 'red'
            return 'red'
        elif blue_shapes > red_shapes:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        for color in [first_player, second_player]:
            shape_counts = {"circle": 0, "square": 0, "triangle": 0}
            for slot in self.slots_for_shapes:
                if slot and slot["color"] == color:
                    shape_counts[slot["shape"]] += 1
           
            total_produced = 0
            for shape, count in shape_counts.items():
                pairs = count // 2
                if pairs > 0:
                    for _ in range(pairs):
                        await game_utilities.produce_shape_for_player(
                            game_state, game_action_container_stack, send_clients_log_message, 
                            send_clients_available_actions, send_clients_game_state, 
                            color, 1, shape, self.name
                        )
                    total_produced += pairs
                    await send_clients_log_message(f"{color} produces {pairs} {shape}(s) from {self.name}")
           
            sets = min(shape_counts.values())
            bonus_points = sets * total_produced * 3
            if bonus_points > 0:
                game_state["points"][color] += bonus_points
                await send_clients_log_message(f"{color} gains {bonus_points} points from {self.name} ({sets} sets, {total_produced} shapes produced)")

        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{ruler} is the ruler of {self.name}")