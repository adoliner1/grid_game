import asyncio
import game_action_container
import game_utilities
import game_constants
from .status import Status

class FireBrand(Status):
    def __init__(self, duration, player_with_status):
        super().__init__(
            name="Fire Brand",
            description="After you exile, trigger effects as if you also burned",
            duration=duration,
            player_with_status=player_with_status
        )

    def setup_listener(self, game_state):
        listener_name = f"{self.name}_{self.player_with_status}"
        game_state["listeners"]["on_exile"][listener_name] = self.on_exile_effect

    def cleanup_listener(self, game_state):
        listener_name = f"{self.name}_{self.player_with_status}"
        del game_state["listeners"]["on_exile"][listener_name]

    async def on_exile_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        color_of_player = data.get('exiler')
        disciple_exiled = data.get('disciple')['disciple']
        color_of_disciple_exiled = data.get('disciple')['color']
        index_of_tile_exiled_from = data.get('index_of_tile_exiled_from')
        
        if (color_of_player == self.player_with_status):
            await send_clients_log_message(f"{self.player_with_status} has {self.name} and also burns")
            await game_utilities.call_listener_functions_for_event_type(game_state,
                                                                        game_action_container_stack,
                                                                        send_clients_log_message,
                                                                        get_and_send_available_actions,
                                                                        send_clients_game_state,
                                                                        "on_burn", 
                                                                        burner=color_of_player,
                                                                        disciple=disciple_exiled,
                                                                        color=color_of_disciple_exiled,
                                                                        index_of_tile_burned_at=index_of_tile_exiled_from)
