import game_utilities
import game_constants
from tiles.tile import Tile

class Saturn(Tile):
    def __init__(self):
        super().__init__(
            name="Saturn",
            description = f"Ruling Criteria: 3 or more shapes\nRuling Benefits: You may use this tile to burn one of your triangles here to produce 2 squares",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "triangle" and slot["color"] == ruler:
                return True
        
        return False

    def determine_ruler(self, game_state):
        red_count = 0
        blue_count = 0

        for slot in self.slots_for_shapes:
            if slot:
                if slot["color"] == "red":
                    red_count += 1
                elif slot["color"] == "blue":
                    blue_count += 1
        if red_count >= 3:
            self.ruler = 'red'
            return 'red'
        elif blue_count >= 3:
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
        
        triangle_found = False
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "triangle" and slot["color"] == ruler:
                await send_clients_log_message(f"{self.name} is used")                
                await self.burn_shape_at_index(game_state, i, send_clients_log_message)
                triangle_found = True
                break
        
        if not triangle_found:
            await send_clients_log_message(f"No triangle to burn on {self.name}")
            return False
        
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, 2, 'square', self.name)

        return True
