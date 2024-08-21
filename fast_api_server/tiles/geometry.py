import game_utilities
import game_constants
from tiles.tile import Tile

class Geometry(Tile):
    def __init__(self):
        super().__init__(
            name="Geometry",
            type="Producer",
            description="7 power: At the start of a round, produce 1 triangle\nRuler: Most Power, minimum 10. Produce another one",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 10:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 10:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.determine_power()
        ruler = self.determine_ruler(game_state)

        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            triangles_to_produce = 0
            if self.power_per_player[player] >= 7:
                triangles_to_produce += 1
                if player == ruler:
                    triangles_to_produce += 1

            for _ in range(triangles_to_produce):
                await game_utilities.produce_shape_for_player(
                    game_state, 
                    game_action_container_stack, 
                    send_clients_log_message, 
                    send_clients_available_actions, 
                    send_clients_game_state, 
                    player, 
                    1,
                    'triangle', 
                    self.name
                )
