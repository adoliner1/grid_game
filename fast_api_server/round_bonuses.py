from game_utilities import *

class RoundBonus:
    def __init__(self, name, description, listener_type):
        self.name = name
        self.description = description
        self.listener_type = listener_type

    def setup(self, game_state):
        game_state["listeners"][self.listener_type][self.name] = self.run_effect

    def cleanup(self, game_state):
        del game_state["listeners"][self.listener_type][self.name]

    def serialize(self):
        return self.description

class PointsPerCircle(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Circle",
            description = "Gain 1 point when you place a circle",
            listener_type="on_place",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        shape = data.get('shape')

        if (shape == "circle"):
            game_state["points"][placer] += 1
            await send_clients_log_message(f"{placer} gets 1 point for placing a circle (round bonus)")

class PointsPerSquare(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Square",
            description = "Gain 2 points when you place a square",
            listener_type="on_place",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        shape = data.get('shape')

        if (shape == "square"):
            game_state["points"][placer] += 2
            await send_clients_log_message(f"{placer} gets 2 points for placing a square (round bonus)")

class PointsPerTriangle(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Triangle",
            description = "Gain 3 points when you place a triangle",
            listener_type="on_place",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        placer = data.get('placer')
        shape = data.get('shape')

        if (shape == "triangle"):
            game_state["points"][placer] += 3
            await send_clients_log_message(f"{placer} gets 3 points for placing a triangle (round bonus)")

class PointsPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Row",
            description = "At the end of the round, if you rule all 3 tiles in a row, +10 points",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_rows = determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = determine_how_many_full_rows_player_rules(game_state, "blue")

        if red_complete_rows > 0:
            points_to_gain = 10*red_complete_rows
            game_state["points"]["red"] += points_to_gain
            await send_clients_log_message(f"red gets {points_to_gain} points for round bonus")

        if blue_complete_rows > 0:
            points_to_gain = 10*blue_complete_rows
            game_state["points"]["blue"] += points_to_gain
            await send_clients_log_message(f"blue gets {points_to_gain} points for round bonus") 

class PointsPerColumn(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Column",
            description = "At the end of the round, if you rule all 3 tiles in a column, +10 points",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_columns = determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = determine_how_many_full_columns_player_rules(game_state, "blue")

        if red_complete_columns > 0:
            points_to_gain = 10 * red_complete_columns
            game_state["points"]["red"] += points_to_gain
            await send_clients_log_message(f"red gets {points_to_gain} points for round bonus")

        if blue_complete_columns > 0:
            points_to_gain = 10 * blue_complete_columns
            game_state["points"]["blue"] += points_to_gain
            await send_clients_log_message(f"blue gets {points_to_gain} points for round bonus")

class PointsPerTileRuled(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Tile Ruled",
            description = "At the end of the round, gain 2 points for each tile you rule",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "red")
        blue_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "blue")

        if red_tiles_ruled > 0:
            points_to_gain = 2 * red_tiles_ruled
            game_state["points"]["red"] += points_to_gain
            await send_clients_log_message(f"Red gets {points_to_gain} points for ruling {red_tiles_ruled} tile(s)")

        if blue_tiles_ruled > 0:
            points_to_gain = 2 * blue_tiles_ruled
            game_state["points"]["blue"] += points_to_gain
            await send_clients_log_message(f"Blue gets {points_to_gain} points for ruling {blue_tiles_ruled} tile(s)")
