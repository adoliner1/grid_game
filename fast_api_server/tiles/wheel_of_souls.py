import game_utilities
import game_constants
from tiles.tile import Tile

class WheelOfSouls(Tile):
    def __init__(self):
        super().__init__(
            name="Wheel of Souls",
            type="Giver",
            minimum_influence_to_rule=6,
            description=f"At the __end of each round__, ^^burn^^ each disciple here and [[receive]] the next most influential disciple. sages becomes followers. When they do, the owner [[receives]] 2 more follower here",
            number_of_slots=10,
            influence_tiers=[],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        await send_clients_log_message(f"Applying end of round effect for **{self.name}**")
        
        for i in range(len(self.slots_for_disciples)):
            if self.slots_for_disciples[i]:
                current_disciple = self.slots_for_disciples[i]["disciple"]
                player_color = self.slots_for_disciples[i]["color"]
                
                await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), i)
                
                if current_disciple == "follower":
                    new_disciple = "acolyte"
                elif current_disciple == "acolyte":
                    new_disciple = "sage"
                else:
                    new_disciple = "follower"
                
                await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, self, new_disciple)

                if new_disciple == "follower":
                    await send_clients_log_message(f"A sage became a follower on **{self.name}**")
                    await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, self, new_disciple)
                    await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_color, self, new_disciple)