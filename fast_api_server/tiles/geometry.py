import game_utilities
import game_constants
from tiles.tile import Tile

class Geometry(Tile):
    def __init__(self):
        super().__init__(
            name="Geometry",
            type="Producer",
            minimum_power_to_rule=3,
            power_tiers=[
                {
                    "power_to_reach_tier": 7,
                    "must_be_ruler": False,
                    "description": "At the __start of a round__, ++produce++ 1 triangle",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
                {
                    "power_to_reach_tier": 10,
                    "must_be_ruler": True,
                    "description": "At the __start of a round__, ++produce++ 1 triangle",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
            ],
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        self.determine_power()
        ruler = self.determine_ruler(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            triangles_to_produce = 0
            if self.power_per_player[player] >= 7:
                triangles_to_produce += 1
            if self.power_per_player[player] >= 10 and player == ruler:
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
                    self.name,
                    True
                )