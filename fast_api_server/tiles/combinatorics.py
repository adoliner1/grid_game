import game_utilities
import game_constants
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            description = f"Ruling Criteria: Most shapes\nRuling Benefits: At the end of the round, per pair here, produce 1 shape of that type",
            number_of_slots=9,
        )

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
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler is None:
            return

        pair_counts = {"circle": 0, "square": 0, "triangle": 0}
        for slot in self.slots_for_shapes:
            if slot and slot["color"] == ruler:
                shape = slot["shape"]
                pair_counts[shape] += 1

        for shape, count in pair_counts.items():
            pairs = count // 2
            if pairs > 0:
                await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, pairs, shape, self.name)