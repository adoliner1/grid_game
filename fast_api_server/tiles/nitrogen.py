import game_utilities
import game_constants
from tiles.tile import Tile

class Nitrogen(Tile):
    def __init__(self):
        super().__init__(
            name="Nitrogen",
            type="Giver/Scorer",
            description=f"At the end of a round, for each triangle you have here, receive a square and a circle here\nAction: burn a set here for +5 points\nRuler: Most Shapes. At the end of the game +7 points",
            number_of_slots=11,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == whose_turn_is_it)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == whose_turn_is_it)
        
        return circle_count >= 1 and square_count >= 1 and triangle_count >= 1

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
        red_triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red" and slot["shape"] == "triangle")
        blue_triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue" and slot["shape"] == "triangle")

        first_player = game_state["first_player"]
        second_player = 'red' if first_player == 'blue' else 'blue'

        first_player_triangles = red_triangle_count if first_player == 'red' else blue_triangle_count
        second_player_triangles = blue_triangle_count if first_player == 'red' else red_triangle_count

        for _ in range(first_player_triangles):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, first_player, self, 'square')
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, first_player, self, 'circle')

        for _ in range(second_player_triangles):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, second_player, self, 'square')
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, second_player, self, 'circle')

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]  
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == game_action_container.whose_action)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == game_action_container.whose_action)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == game_action_container.whose_action)
        
        if circle_count < 1 or square_count < 1 or triangle_count < 1:
            await send_clients_log_message(f"Not enough shapes to burn on {self.name}")
            return False
        
        nitrogen_tile_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        shapes_burned = {'circle': 0, 'square': 0, 'triangle': 0}
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == game_action_container.whose_action and shapes_burned[slot["shape"]] < 1:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, nitrogen_tile_index, i)
                shapes_burned[slot["shape"]] += 1
                if all(count == 1 for count in shapes_burned.values()):
                    break
        
        await send_clients_log_message(f"{self.name} is used")
        
        game_state["points"][game_action_container.whose_action] += 5
        await send_clients_log_message(f"{game_action_container.whose_action} gains 5 points")

        return True

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} gives 7 points to {ruler}")
            game_state["points"][ruler] += 7
