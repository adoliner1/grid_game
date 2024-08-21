import game_utilities
import game_constants
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            type="Producer/Scorer",
            description="At the end of a round, for each same-shape pair you have here, produce 1 shape of that type\nRuler: Most sets. +3 points per shape you produce this way",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        red_sets = game_utilities.count_sets_on_tile_for_color(self, "red")
        blue_sets = game_utilities.count_sets_on_tile_for_color(self, "blue")
        
        if red_sets > blue_sets:
            self.ruler = 'red'
            return 'red'
        elif blue_sets > red_sets:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
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
                    await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, color, pairs, shape, self.name)
                    total_produced += pairs
                    await send_clients_log_message(f"{color} produces {pairs} {shape}(s) from {self.name}")
            
            if color == ruler:
                bonus_points = total_produced * 3
                game_state["points"][color] += bonus_points
                await send_clients_log_message(f"{color} gains {bonus_points} bonus points as the ruler of {self.name}")