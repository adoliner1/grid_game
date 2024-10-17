import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class FieldsOfHermes(Tile):
    def __init__(self):
        super().__init__(
            name="Fields of Hermes",
            type="Giver",
            minimum_influence_to_rule=5,
            description="When you move on to or adjacent to Fields of Hermes, [[receive]] a follower at Fields of Hermes",
            number_of_slots=12,
            influence_tiers=[],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_leader_move"][self.name] = self.on_leader_move_effect

    async def on_leader_move_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        color = data.get('leader_color_moved')
        index_of_tile_moved_to = data.get('to_tile_index')
        
        fields_of_hermes_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if index_of_tile_moved_to == fields_of_hermes_index or game_utilities.determine_if_directly_adjacent(fields_of_hermes_index, index_of_tile_moved_to):
            await game_utilities.player_receives_a_disciple_on_tile(
                game_state, game_action_container_stack, send_clients_log_message,
                get_and_send_available_actions, send_clients_game_state,
                color, self, 'follower'
            )