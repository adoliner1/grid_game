import game_utilities
import game_constants
import math


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

'''
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
'''

class PointsPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Row",
            description = "If you rule all 3 tiles in a row, +10 points",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

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
            description = "If you rule all 3 tiles in a column, +10 points",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

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
            description = "Gain 2 points for each tile you rule",
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

class CirclesPerPresence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Circles for 2 Presence",
            description="Produce circles equal to your presence/2 (round down)",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            
            await send_clients_log_message(f"Round bonus gives circles for presence:")


class CirclesPerPeakPower(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Circles for 2 Peak-Power",
            description="Produce circles equal to your peak power/2 (round down)",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_power_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Round bonus gives circles for peak power:")
        for player in [first_player, second_player]:
            peak_power = game_state["peak_power"][player]

            
class CirclesForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Circles for Longest Chain",
            description="Produce circles equal to the length of your longest connected chain of ruled tiles",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        
        for player in [first_player, second_player]:
            player_color = "red" if player == "red" else "blue"
            longest_chain = longest_chains[player_color]
            
            await send_clients_log_message(f"Round bonus gives circles for longest chain:")


class PointsForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Points for Longest Chain",
            description="Gain points equal to the length*3 of your longest connected chain of ruled tiles",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        
        for player in [first_player, second_player]:
            points_to_award = longest_chains[player]*3
            game_state["points"][player] += points_to_award
            await send_clients_log_message(f"{player} gains {points_to_award} points from round bonus. Longest chain: {longest_chains[player]}")


class PointsPerPresence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for Presence",
            description="Gain points equal to your presence",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            points_to_award = presence
            
            game_state["points"][player] += points_to_award
            await send_clients_log_message(f"{player} gains {points_to_award} points from {self.name} (presence: {presence})")

class PointsPerPeakPower(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for Peak Power",
            description="Gain points equal to your peak power",
            listener_type="end_of_round",
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_power_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            peak_power = game_state["peak_power"][player]
            points_to_award = peak_power
            
            game_state["points"][player] += points_to_award
            await send_clients_log_message(f"{player} gains {points_to_award} points from {self.name} (peak power: {peak_power})")


