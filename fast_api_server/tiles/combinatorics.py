import game_utilities
import game_constants
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            type="Producer/Scorer",
            minimum_power_to_rule=3,
            description="At the __end of a round__, for each unique, same-shape pair you have here, ++produce++ one circle\nFor each set you have here, +3 points per circle you ++produced++ this way",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        for color in [first_player, second_player]:
            shape_counts = {"circle": 0, "square": 0, "triangle": 0}
            for slot in self.slots_for_shapes:
                if slot and slot["color"] == color:
                    shape_counts[slot["shape"]] += 1
           
            total_produced = 0
            for shape, count in shape_counts.items():
                unique_pairs = min(count // 2, 1)
                if unique_pairs  > 0:
                    for _ in range(unique_pairs):
                        await game_utilities.produce_shape_for_player(
                            game_state, game_action_container_stack, send_clients_log_message, 
                            get_and_send_available_actions, send_clients_game_state, 
                            color, 1, shape, self.name, True
                        )
                    total_produced += unique_pairs
                    await send_clients_log_message(f"{color} produces {unique_pairs} {shape}(s) from {self.name}")
           
            sets = min(shape_counts.values())
            bonus_points = sets * total_produced * 3
            if bonus_points > 0:
                game_state["points"][color] += bonus_points
                await send_clients_log_message(f"{color} gains {bonus_points} points from {self.name} ({sets} sets, {total_produced} circles produced)")

        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{ruler} is the ruler of {self.name}")