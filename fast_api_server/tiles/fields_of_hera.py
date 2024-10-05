import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class FieldsOfHera(Tile):
    def __init__(self):
        super().__init__(
            name="Fields of Hera",
            type="Giver",
            minimum_influence_to_rule=6,
            description="When you ((recruit)) or [[receive]] a disciple adjacent to Fields of Hera, [[receive]] a follower at Fields of Hera",
            number_of_slots=12,
            influence_tiers=[],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_recruit"][self.name] = self.on_recruit_effect
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, data, "recruited")

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, data, "received")

    async def handle_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, data, action_type):
        actor = data.get('recruiter') if action_type == "recruited" else data.get('receiver')
        index_of_tile_acted_at = data.get('index_of_tile_recruited_at') if action_type == "recruited" else data.get('index_of_tile_received_at')
        
        fields_of_hera_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if not game_utilities.determine_if_directly_adjacent(fields_of_hera_index, index_of_tile_acted_at):
            return

        await send_clients_log_message(f"**{self.name}** effect runs")
        await game_utilities.player_receives_a_disciple_on_tile(
            game_state, game_action_container_stack, send_clients_log_message,
            get_and_send_available_actions, send_clients_game_state,
            actor, self, 'follower'
        )

