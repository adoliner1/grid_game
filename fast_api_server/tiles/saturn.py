import game_utilities
import game_constants
from tiles.tile import Tile

class Saturn(Tile):
    def __init__(self):
        super().__init__(
            name="Saturn",
            type="Producer",
            description="**Ruler, +2 Power Differential, Minimum 4 Power, Action:** Once per round, ^^burn^^ one of your triangles here to ++produce++ 2 squares",
            number_of_slots=5,
            is_on_cooldown=False
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        red_power = self.power_per_player["red"]
        blue_power = self.power_per_player["blue"]
        if red_power >= 4 and red_power >= blue_power + 2:
            self.ruler = 'red'
            return 'red'
        elif blue_power >= 4 and blue_power >= red_power + 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
        if whose_turn_is_it != ruler or self.is_on_cooldown:
            return False
        
        return any(slot and slot["shape"] == "triangle" and slot["color"] == ruler 
                   for slot in self.slots_for_shapes)

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        if not ruler:
            await send_clients_log_message(f"No ruler determined for {self.name} cannot use")
            return False
        
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Non-ruler tried to use {self.name}")
            return False
        
        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["shape"] == "triangle" and slot["color"] == ruler:
                await send_clients_log_message(f"{self.name} is used")                
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), i)
                for _ in range(2):
                    await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, 1, 'square', self.name, True)
                self.is_on_cooldown = True
                return True
        
        await send_clients_log_message(f"No triangle to burn on {self.name}")
        return False