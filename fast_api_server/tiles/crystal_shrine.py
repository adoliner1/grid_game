import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class CrystalShrine(Tile):
    def __init__(self):
        super().__init__(
            name="Crystal Shrine",
            type="Generator",
            number_of_slots=5,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 9,
                    "must_be_ruler": True,                     
                    "description": "At the __end of each round__, if Crystal Shrine is full, +7 power",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False, 
                    "has_cooldown": False,
                }
            ]
        )

    def modify_expected_incomes(self, game_state):
        self.determine_influence()
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            power_to_gain = 0
            if ruler == player and self.influence_per_player[player] >= self.influence_tiers[0]['influence_to_reach_tier'] and None not in self.slots_for_disciples:
                power_to_gain += 6
            
            if power_to_gain > 0:
                game_state['expected_power_incomes'][player] += power_to_gain

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)    

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        self.determine_influence()
        ruler = self.determine_ruler(game_state)
        for player in game_constants.player_colors:
            power_to_gain = 0
            if ruler == player and self.influence_per_player[player] >= self.influence_tiers[0]['influence_to_reach_tier'] and None not in self.slots_for_disciples:
                power_to_gain += 6
            
            if power_to_gain > 0:
                await send_clients_log_message(f'**{self.name}** gives {power_to_gain} power to {player}')  
                game_state['power'][player] += power_to_gain