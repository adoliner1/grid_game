import game_utilities
import game_constants
from tiles.tile import Tile

class PlainsOfHermes(Tile):
    def __init__(self):
        super().__init__(
            name="Plains of Hermes",
            type="Leader-Movement",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "At the __end of each round__ +1 leader_movement",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "leader_must_be_present": False, 
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_expected_incomes(self, game_state):
        self.determine_influence()
        ruler = self.determine_ruler(game_state)
        leader_movement_to_gain = 0
        if ruler and self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']:
            leader_movement_to_gain += 1
        
        if leader_movement_to_gain > 0:
            game_state['expected_leader_movement_incomes'][ruler] += leader_movement_to_gain

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_influence()
        ruler = self.determine_ruler(game_state)
        leader_movement_to_gain = 0
        if ruler and self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']:
            leader_movement_to_gain += 1

            if leader_movement_to_gain > 0:
                await send_clients_log_message(f'**{self.name}** gives {leader_movement_to_gain} power to {ruler}')  
                game_state['leader_movement'][ruler] += 1