import game_utilities
import game_constants
from tiles.tile import Tile

class Boron(Tile):
    def __init__(self):
        super().__init__(
            name="Boron",
            type="Giver",
            description = "At the __end of a round__, per square you have here, [[receive]] a circle here.",
            number_of_slots=11,
            minimum_influence_to_rule=3,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Running end of round effect for {self.name}")
        for player in [first_player, second_player]:
            square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player and slot["shape"] == "square")
            for _ in range(square_count):
                await game_utilities.player_receives_a_shape_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    get_and_send_available_actions, send_clients_game_state, 
                    player, self, 'circle'
                )