import game_utilities
import game_constants
from tiles.tile import Tile

class SolarArray(Tile):
    def __init__(self):
        super().__init__(
            name="Solar Array",
            type="Scorer",
            description="**Ruler, Most Shapes, Minimum 2, Action:** ^^Burn^^ all your shapes here, then:\n**If your Peak Power >= 6:** +3 points\n**>= 10:** +7 points\n**>= 14:** +12 points",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")

        if red_count > blue_count and red_count >= 2:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count and blue_count >= 2:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def is_useable(self, game_state):
        ruler = self.determine_ruler(game_state)
        return ruler is not None and ruler == game_state["whose_turn_is_it"]

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)

        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"{game_action_container.whose_action} is not the ruler of {self.name} and cannot use it")
            return False

        solar_array_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        shapes_burned = 0

        for i, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == ruler:
                await game_utilities.burn_shape_at_tile_at_index(
                    game_state, game_action_container_stack, send_clients_log_message,
                    send_clients_available_actions, send_clients_game_state,
                    solar_array_index, i
                )
                shapes_burned += 1

        await send_clients_log_message(f"{ruler} burned {shapes_burned} shapes on {self.name}")

        peak_power = game_state["peak_power"][ruler]
        points_gained = 0

        if peak_power >= 14:
            points_gained = 12
        elif peak_power >= 10:
            points_gained = 7
        elif peak_power >= 6:
            points_gained = 3

        if points_gained > 0:
            game_state["points"][ruler] += points_gained
            await send_clients_log_message(f"{ruler} gains {points_gained} points from {self.name}")

        return True