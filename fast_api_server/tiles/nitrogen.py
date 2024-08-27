import game_utilities
import game_constants
from tiles.tile import Tile

class Nitrogen(Tile):
    def __init__(self):
        super().__init__(
            name="Nitrogen",
            type="Giver/Scorer",
            description="At the __end of a round__, at Nitrogen, per triangle you have, [[receive]] a square and a circle\n**Action:** ^^Burn^^ a set here for +4 points\n**Ruler: Most Shapes**",
            number_of_slots=11,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == whose_turn_is_it)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == whose_turn_is_it)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == whose_turn_is_it)
        
        return circle_count >= 1 and square_count >= 1 and triangle_count >= 1

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

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = 'red' if first_player == 'blue' else 'blue'

        for player in [first_player, second_player]:
            triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player and slot["shape"] == "triangle")
            
            for _ in range(triangle_count):
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player, self, 'square')
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player, self, 'circle')
            
            if triangle_count > 0:
                await send_clients_log_message(f"{player} receives {triangle_count} square(s) and {triangle_count} circle(s) on {self.name}")

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]  
        player = game_action_container.whose_action
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == player)
        square_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "square" and slot["color"] == player)
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "triangle" and slot["color"] == player)
        
        if circle_count < 1 or square_count < 1 or triangle_count < 1:
            await send_clients_log_message(f"Not enough shapes to burn a set on {self.name}")
            return False
        
        nitrogen_tile_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        shapes_burned = {'circle': 0, 'square': 0, 'triangle': 0}
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == player and shapes_burned[slot["shape"]] < 1:
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, nitrogen_tile_index, i)
                shapes_burned[slot["shape"]] += 1
                if all(count == 1 for count in shapes_burned.values()):
                    break
        
        await send_clients_log_message(f"{player} burns a set on {self.name}")
        
        game_state["points"][player] += 4
        await send_clients_log_message(f"{player} gains 4 points from burning a set on {self.name}")

        return True