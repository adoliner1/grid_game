import game_utilities
import game_constants
from tiles.tile import Tile

class Boron(Tile):
    def __init__(self):
        super().__init__(
            name="Boron",
            type="Giver",
            description = "At the end of a round, per square you have here, receive a circle here.\nRuler: Most Shapes. +3 points at the end of the game",
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
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Running end of round effect for {self.name}")
        for player in [first_player, second_player]:
            square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player and slot["shape"] == "square")
            for _ in range(square_count):
                await game_utilities.player_receives_a_shape_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    send_clients_available_actions, send_clients_game_state, 
                    player, self, 'circle'
                )

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3