import game_utilities
import game_constants
from tiles.tile import Tile

class Boron(Tile):
    def __init__(self):
        super().__init__(
            name="Boron",
            description = "At the end of the round, if you have a square here, receive a circle here. The player with more circles here produces 1 circle.\nRuling Criteria: most shapes \nRuling Benefits: At the end of the game, +5 points",
            number_of_slots=11,
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

        red_has_square = False
        blue_has_square = False
        
        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "square":
                    red_has_square = True
                elif slot["color"] == "blue" and slot["shape"] == "square":
                    blue_has_square = True

        if red_has_square:
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', self, 'circle')
            await send_clients_log_message(f"red has a square on {self.name}")
        
        if blue_has_square:
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', self, 'circle')
            await send_clients_log_message(f"blue has a square on {self.name}")

        red_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red" and slot["shape"] == "circle")
        blue_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue" and slot["shape"] == "circle")

        if red_circle_count > blue_circle_count:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'circle', self.name)
            await send_clients_log_message(f"red produces 1 circle for having more circles on {self.name}")
        elif blue_circle_count > red_circle_count:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'circle', self.name)
            await send_clients_log_message(f"blue produces 1 circle for having more circles on {self.name}")

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state,):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5
