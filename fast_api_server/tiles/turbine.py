import game_utilities
import game_constants
from tiles.tile import Tile

class Turbine(Tile):
    def __init__(self):
        super().__init__(
            name="Turbine",
            type="Producer",
            description="**Ruler, Most Shapes, Action:** Once per round, if your peak power is\n>= 6, ++produce++ a circle\n>= 10, a square\n>= 14, a triangle",
            number_of_slots=3,
        )

    def is_useable(self, game_state):
        whose_turn_is_it = game_state["whose_turn_is_it"]
        return self.determine_ruler(game_state) == whose_turn_is_it and not self.is_on_cooldown

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

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        peak_power = game_state["peak_power"][user]

        if self.is_on_cooldown:
            await send_clients_log_message(f"Tried to use {self.name} but it's on cooldown")
            return False
        
        if self.determine_ruler(game_state) != user:
            await send_clients_log_message(f"Tried to use {self.name} but they don't rule it")
            return False

        await send_clients_log_message(f"{user} is using {self.name}")

        if peak_power >= 14:
            await game_utilities.produce_shape_for_player(
                game_state, game_action_container_stack, send_clients_log_message,
                send_clients_available_actions, send_clients_game_state,
                user, 1, "triangle", self.name, True
            )

        elif peak_power >= 10:
            await game_utilities.produce_shape_for_player(
                game_state, game_action_container_stack, send_clients_log_message,
                send_clients_available_actions, send_clients_game_state,
                user, 1, "square", self.name, True
            )

        elif peak_power >= 6:
            await game_utilities.produce_shape_for_player(
                game_state, game_action_container_stack, send_clients_log_message,
                send_clients_available_actions, send_clients_game_state,
                user, 1, "circle", self.name, True
            )

        self.is_on_cooldown = True
        return True