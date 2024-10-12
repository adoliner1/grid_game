import asyncio
import game_action_container
import game_utilities
import game_constants
from .status import Status

class HerasGift(Status):
    def __init__(self, duration, player_with_status):
        super().__init__(
            name="Heras Gift",
            description="After you recruit, trigger effects as if you also received",
            duration=duration,
            player_with_status=player_with_status
        )

    def setup_listener(self, game_state):
        listener_name = f"{self.name}_{self.player_with_status}"
        game_state["listeners"]["on_recruit"][listener_name] = self.on_recruit_effect

    def cleanup_listener(self, game_state):
        listener_name = f"{self.name}_{self.player_with_status}"
        del game_state["listeners"]["on_recruit"][listener_name]

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        color_of_player = data.get('recruiter')
        disciple_recruited = data.get('disciple')
        index_of_tile_recruited_at = data.get('index_of_tile_recruited_at')
        slot_index_recruited_at = data.get('slot_index_recruited_at')
       
        if color_of_player == self.player_with_status:
            await send_clients_log_message(f"{self.player_with_status} has {self.name} and also receives")
            await game_utilities.call_listener_functions_for_event_type(
                game_state,
                game_action_container_stack,
                send_clients_log_message,
                get_and_send_available_actions,
                send_clients_game_state,
                "on_receive",
                receiver=color_of_player,
                disciple=disciple_recruited,
                index_of_tile_received_at=index_of_tile_recruited_at,
                index_of_slot_received_at=slot_index_recruited_at
            )