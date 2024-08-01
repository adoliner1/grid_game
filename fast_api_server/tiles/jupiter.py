import game_utilities
import game_constants
from tiles.tile import Tile

class Jupiter(Tile):
    def __init__(self):
        super().__init__(
            name="Jupiter",
            description = f"Ruling Criteria: 3 or more shapes\nRuling Benefits: You may use this tile to burn one of your squares here to produce a triangle. At the end of the game +2 points",
            number_of_slots=5,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)

        if whose_turn_is_it != ruler:
            return False
        
        for slot in self.slots_for_shapes:
            if slot and slot["shape"] == "square" and slot["color"] == ruler:
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
        
        square_found = False
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "square" and slot["color"] == ruler:
                await send_clients_log_message(f"{self.name} is used")                
                await self.burn_shape_at_index(game_state, i, send_clients_log_message)
                square_found = True
                break
        
        if not square_found:
            await send_clients_log_message(f"No square to burn on {self.name}")
            return False
        
        if (ruler == 'red'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'red', 1, 'triangle', self.name)
        elif (ruler == 'blue'):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, 'blue', 1, 'triangle', self.name)

        return True

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if (ruler != None):
            await send_clients_log_message(f"{self.name} gives 2 points to {ruler}")
            game_state["points"][ruler] += 2
