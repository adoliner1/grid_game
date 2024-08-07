import game_utilities
import game_constants
from tiles.tile import Tile

class Carbon(Tile):
    def __init__(self):
        super().__init__(
            name="Carbon",
            description=f"At the end of the round, per pair of circles you have here, receive a circle here. Anyone can use this tile to burn 3 of their circles here to produce a triangle\nRuling Criteria: most squares\nRuling Benefits: At the end of the game +5 points",
            number_of_slots=12,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        number_of_circles_current_player_has_here = 0
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it:
                number_of_circles_current_player_has_here += 1

        return number_of_circles_current_player_has_here >= 3 

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red" and slot["shape"] == "square":
                    red_count += 1
                elif slot["color"] == "blue" and slot["shape"] == "square":
                    blue_count += 1
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        red_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red" and slot["shape"] == "circle")
        blue_circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue" and slot["shape"] == "circle")

        red_pairs = red_circle_count // 2
        blue_pairs = blue_circle_count // 2

        first_player = game_state["first_player"]
        second_player = 'red' if first_player == 'blue' else 'blue'

        first_player_pairs = red_pairs if first_player == 'red' else blue_pairs
        second_player_pairs = blue_pairs if first_player == 'red' else red_pairs

        for _ in range(first_player_pairs):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, first_player, self, 'circle')

        for _ in range(second_player_pairs):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, second_player, self, 'circle')

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == game_action_container.whose_action)
        
        if circle_count < 3:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False
        
        circles_burned = 0
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "circle" and slot["color"] == game_action_container.whose_action:
                await self.burn_shape_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, i)
                circles_burned += 1
                if circles_burned == 3:
                    break

        if circles_burned < 3:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, game_action_container.whose_action, 1, 'triangle', self.name)
        return True

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 5 points to {ruler}")
            game_state["points"][ruler] += 5
