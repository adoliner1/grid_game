import game_utilities
import game_constants
from tiles.tile import Tile

class Calculus(Tile):
    def __init__(self):
        super().__init__(
            name="Calculus",
            description = f"Ruling Criteria: Most shapes, minimum 2, and at least 1 square\nRuling Benefits: At the start of the round, produce 1 square. At the end of the game +3 points",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0
        red_square_count = 0
        blue_square_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                    if slot["shape"] == "square":
                        red_square_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
                    if slot["shape"] == "square":
                        blue_square_count += 1

        if red_count >= 2 and red_square_count >= 1 and red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 2 and blue_square_count >= 1 and blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'square', self.name)
        elif (ruler == 'blue'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'square', self.name)
            
    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3