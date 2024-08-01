import game_utilities
import game_constants
from tiles.tile import Tile

class Algebra(Tile):
    def __init__(self):
        super().__init__(
            name="Algebra",
            description = f"Ruling Criteria: 2 or more shapes\nRuling Benefits: At the start of the round, produce 1 circle. At the end of the game +2 points",
            number_of_slots=5,
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
        if red_count > blue_count and red_count >= 2:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count and blue_count >= 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'circle', self.name)
        elif (ruler == 'blue'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'circle', self.name)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 2 points to {ruler}")
            game_state["points"][ruler] += 2