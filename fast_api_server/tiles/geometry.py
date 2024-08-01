import game_utilities
import game_constants
from tiles.tile import Tile

class Geometry(Tile):
    def __init__(self):
        super().__init__(
            name="Geometry",
            description = f"Ruling Criteria: 4 or more shapes\nRuling Benefits: At the start of the round, produce 1 triangle. At the end of the game +2 points",
            number_of_slots=7,
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
        if red_count >= 4:
            self.ruler = 'red'
        elif blue_count >= 4:
            self.ruler = 'blue'
        else:
            self.ruler = None
        
        return self.ruler

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)

        if (ruler == 'red'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'triangle', self.name)
        elif (ruler == 'blue'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'triangle', self.name)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 2 points to {ruler}")
            game_state["points"][ruler] += 2