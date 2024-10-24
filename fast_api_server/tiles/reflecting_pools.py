import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class ReflectingPools(Tile):
    def __init__(self):
        super().__init__(
            name="Reflecting Pools",
            type="Giver",
            minimum_influence_to_rule=6,
            description="When you [[receive]] a discple within 2 tiles of Reflecting Pools (but not at it), [[receive]] a copy of it here",
            number_of_slots=6,
            influence_tiers=[],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')
        disciple_type = data.get('disciple')
        reflecting_pools_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        # Don't trigger if the receive happened on this tile
        if index_of_tile_received_at == reflecting_pools_index:
            return

        # Check if the receive happened within 2 tiles
        distance = game_utilities.get_distance_between_tile_indexes(reflecting_pools_index, index_of_tile_received_at)
        if distance > 2:
            return

        await send_clients_log_message(f"**{self.name}** copies the {disciple_type}")
        
        await game_utilities.player_receives_a_disciple_on_tile(
            game_state, game_action_container_stack, send_clients_log_message,
            get_and_send_available_actions, send_clients_game_state,
            receiver, self, disciple_type
        )