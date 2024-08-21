import game_utilities
import game_constants
from tiles.tile import Tile

class Carbon(Tile):
    def __init__(self):
        super().__init__(
            name="Carbon",
            type="Giver/Scorer",
            description=f"At the end of a round, per circle you have here, receive a circle here. Action: Burn 3 of your circles here to receive a triangle here\nRuler: Most Shapes. +3 points at the end of the game",
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
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
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
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        first_player_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == first_player and slot["shape"] == "circle")
        second_player_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == second_player and slot["shape"] == "circle")

        for _ in range(first_player_count):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, first_player, self, 'circle')

        for _ in range(second_player_count):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, second_player, self, 'circle')

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == game_action_container.whose_action)
        
        if circle_count < 3:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        circles_burned = 0
        for index, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "circle" and slot["color"] == game_action_container.whose_action:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), index)
                circles_burned += 1
                if circles_burned == 3:
                    break

        if circles_burned < 3:
            await send_clients_log_message(f"Not enough circles were burned on {self.name}")
            return False
        
        await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_action_container.whose_action, self, 'triangle')
        return True

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 3 points to {ruler}")
            game_state["points"][ruler] += 3
