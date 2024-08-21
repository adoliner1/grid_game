import game_utilities
import game_constants
from tiles.tile import Tile

class Pluto(Tile):
    def __init__(self):
        super().__init__(
            name="Pluto",
            type="Producer/Scorer",
            description = "Ruler: Most Shapes, Action: Burn 2 circles here to produce a square",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        if self.is_on_cooldown:
            return False
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        circle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["shape"] == "circle" and slot["color"] == ruler)
        return circle_count >= 2

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

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]  
        ruler = self.determine_ruler(game_state)
        if not ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False
        
        circles_to_burn = [
            i for i, slot in enumerate(self.slots_for_shapes)
            if slot and slot["shape"] == "circle" and slot["color"] == ruler
        ]

        if len(circles_to_burn) < 2:
            await send_clients_log_message(f"Not enough circles to burn on {self.name}")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        for i in circles_to_burn[:2]:
            await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), i)
        
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_action_container.whose_action, 1, 'square', self.name)
        return True
