import game_utilities
import game_constants
from tiles.tile import Tile

class Ember(Tile):
    def __init__(self):
        super().__init__(
            name="Ember",
            type="Scorer",
            minimum_power_to_rule=3,
            power_tiers=[],
            description=f"You may not ((place)) here\nWhen a shape is ^^burned^^ on a tile, the owner [[receives]] a copy of it here\nAt the __end of a round__, if Ember is full, remove all the shapes. +6 points to whichever player had more",
            number_of_slots=11,
            shapes_which_can_be_placed_on_this=[]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        burned_shape = data.get('shape')
        burned_color = data.get('color')

        await send_clients_log_message(f"{self.name} triggers")
        await game_utilities.player_receives_a_shape_on_tile(
            game_state, 
            game_action_container_stack, 
            send_clients_log_message, 
            get_and_send_available_actions, 
            send_clients_game_state, 
            burned_color, 
            self, 
            burned_shape
        )
        
    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        if all(slot is not None for slot in self.slots_for_shapes):
            red_count = sum(1 for slot in self.slots_for_shapes if slot["color"] == "red")
            blue_count = sum(1 for slot in self.slots_for_shapes if slot["color"] == "blue")
            
            if red_count > blue_count:
                winner = "red"
            elif blue_count > red_count:
                winner = "blue"

            game_state["points"][winner] += 6
            await send_clients_log_message(f"Red had {red_count} on ember, blue had {blue_count}. {winner} gains 6 points. {self.name} is emptied")

            self.slots_for_shapes = [None] * self.number_of_slots