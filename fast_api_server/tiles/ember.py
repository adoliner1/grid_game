import game_utilities
import game_constants
from tiles.tile import Tile

class Ember(Tile):
    def __init__(self):
        super().__init__(
            name="Ember",
            description=f"-5 points when you place here. When a shape is burned from a tile anywhere, Ember receives a copy of it. At the end of each round, if Ember is full, remove all the shapes. +10 points to whichever player had more. Ruling Criteria: Most shapes\nRuling Benefits: none",
            number_of_slots=11,
        )

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")

        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def setup_listener(self, game_state):
        game_state["listeners"]["on_place"][self.name] = self.on_place_effect
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_place_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        index_of_tile_placed_at = data.get('index_of_tile_placed_at')
        
        if game_utilities.find_index_of_tile_by_name(game_state, self.name) == index_of_tile_placed_at:
            game_state["points"][placer] -= 5
            await send_clients_log_message(f"{placer} loses 5 points for placing on {self.name}")

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        burned_shape = data.get('shape')
        burned_color = data.get('color')

        await send_clients_log_message(f"{self.name} triggers")
        await game_utilities.player_receives_a_shape_on_tile(
            game_state, 
            game_action_container_stack, 
            send_clients_log_message, 
            send_clients_available_actions, 
            send_clients_game_state, 
            burned_color, 
            self, 
            burned_shape
        )
        
    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        if all(slot is not None for slot in self.slots_for_shapes):
            red_count = sum(1 for slot in self.slots_for_shapes if slot["color"] == "red")
            blue_count = sum(1 for slot in self.slots_for_shapes if slot["color"] == "blue")
            
            if red_count > blue_count:
                winner = "red"
            elif blue_count > red_count:
                winner = "blue"

            game_state["points"][winner] += 10
            await send_clients_log_message(f"{winner} gains 10 points from {self.name} for having more shapes at the end of the round. {self.name} is emptied")

            self.slots_for_shapes = [None] * self.number_of_slots