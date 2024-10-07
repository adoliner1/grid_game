import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class DukesFête(Tile):
    def __init__(self):
        super().__init__(
            name="Duke's Fête",
            type="Scorer",
            minimum_influence_to_rule=3,
            description="",
            number_of_slots=6,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "At the __end of the round__, gain points equal to the number of disciples you have at adjacent tiles",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,    
                    "leader_must_be_present": False,              
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_expected_incomes(self, game_state):
        ruler = self.determine_ruler(game_state)
        if ruler and self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']:
            index_of_dukes_fete = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            adjacent_tile_indices = game_utilities.get_adjacent_tile_indices(index_of_dukes_fete)
            
            expected_points = sum(
                sum(1 for slot in game_state['tiles'][index].slots_for_disciples if slot and slot['color'] == ruler)
                for index in adjacent_tile_indices
            )
            game_state["expected_points_incomes"][ruler] += expected_points

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler and self.influence_per_player[ruler] >= self.influence_tiers[0]['influence_to_reach_tier']:
            index_of_dukes_fete = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            adjacent_tile_indices = game_utilities.get_adjacent_tile_indices(index_of_dukes_fete)
            
            points_gained = sum(
                sum(1 for slot in game_state['tiles'][index].slots_for_disciples if slot and slot['color'] == ruler)
                for index in adjacent_tile_indices
            )
            
            if points_gained > 0:
                game_state['points'][ruler] += points_gained
                await send_clients_log_message(f"{ruler} gains {points_gained} points from **{self.name}** for disciples at adjacent tiles")