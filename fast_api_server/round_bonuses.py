import game_utilities
import game_constants
import math

class RoundBonus:
    def __init__(self, name, description, listener_type, bonus_type):
        self.name = name
        self.description = description
        self.listener_type = listener_type
        self.bonus_type = bonus_type

    def setup(self, game_state):
        game_state["listeners"][self.listener_type][self.name] = self.run_effect

    def cleanup(self, game_state):
        del game_state["listeners"][self.listener_type][self.name]

    def serialize(self):
        return self.description

class PointsPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Row",
            description = "If you rule all 3 tiles in a row, +10 points",
            listener_type="end_of_round",
            bonus_type="scorer"
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
            bonus_type="scorer"
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
            bonus_type="scorer"
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

class StaminaPerPresence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Stamina for Presence",
            description="Gain stamina equal to your presence/2 (round down)",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            stamina_to_gain = presence/2
            game_state['stamina'][player] += stamina_to_gain
            await send_clients_log_message(f"{player} has {presence} presence and gains {stamina_to_gain}")

class StaminaPerPeakPower(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Stamina for Peak-Power",
            description="Gain stamina equal to your peak power/2 (round down)",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_power_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            peak_power = game_state["peak_power"][player]
            stamina_to_gain = peak_power/2
            game_state['stamina'][player] += stamina_to_gain
            await send_clients_log_message(f"{player} has a peak power of {peak_power} and gains {stamina_to_gain}")
            
class StaminaForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Stamina for Longest Chain",
            description="Gain stamina equal to the length of your longest connected chain of ruled tiles",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        
        for player in [first_player, second_player]:
            player_color = "red" if player == "red" else "blue"
            size_of_longest_chain = longest_chains[player_color]
            stamina_to_gain = size_of_longest_chain
            game_state['stamina'][player] += stamina_to_gain
            await send_clients_log_message(f"{player} has a chain of size of {size_of_longest_chain} and gains {stamina_to_gain}")

class PointsForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Points for Longest Chain",
            description="Gain points equal to the length*3 of your longest connected chain of ruled tiles",
            listener_type="end_of_round",
            bonus_type="scorer"
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
            bonus_type="scorer"
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
            bonus_type="scorer"
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

class StaminaForCorner(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Stamina for Corner",
            description="Gain 3 stamina if your leader is on a corner tile",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            tile_index_of_leader = game_utilities.get_tile_index_of_leader(game_state, player)
            if tile_index_of_leader in game_constants.corner_tiles:
                stamina_to_gain = 3
                game_state['stamina'][player] += stamina_to_gain
                await send_clients_log_message(f"{player} leader is on a corner tile, {game_state['tiles'][tile_index_of_leader].name}, so gains {stamina_to_gain} stamina")

class StaminaPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Stamina Per Completed Row",
            description = "If you rule all 3 tiles in a row, gain 5 stamina",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

        for player, complete_rows in [("red", red_complete_rows), ("blue", blue_complete_rows)]:
            if complete_rows > 0:
                stamina_to_gain = 5 * complete_rows
                game_state["stamina"][player] += stamina_to_gain
                await send_clients_log_message(f"{player} gains {stamina_to_gain} stamina for {complete_rows} completed row(s)")

class StaminaPerColumn(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Stamina Per Completed Column",
            description = "If you rule all 3 tiles in a column, gain 5 stamina",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

        for player, complete_columns in [("red", red_complete_columns), ("blue", blue_complete_columns)]:
            if complete_columns > 0:
                stamina_to_gain = 5 * complete_columns
                game_state["stamina"][player] += stamina_to_gain
                await send_clients_log_message(f"{player} gains {stamina_to_gain} stamina for {complete_columns} completed column(s)")

class StaminaPerTileRuled(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Stamina Per Tile Ruled",
            description = "Gain 1 stamina for each tile you rule",
            listener_type="end_of_round",
            bonus_type="income"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "red")
        blue_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "blue")

        for player, tiles_ruled in [("red", red_tiles_ruled), ("blue", blue_tiles_ruled)]:
            if tiles_ruled > 0:
                stamina_to_gain = tiles_ruled
                game_state["stamina"][player] += stamina_to_gain
                await send_clients_log_message(f"{player} gains {stamina_to_gain} stamina for ruling {tiles_ruled} tile(s)")

class PointsForCorner(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for Corner",
            description="Gain 5 points if your leader is on a corner tile",
            listener_type="end_of_round",
            bonus_type="scorer"
        )

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            tile_index_of_leader = game_utilities.get_tile_index_of_leader(game_state, player)
            if tile_index_of_leader in game_constants.corner_tiles:
                points_to_gain = 5
                game_state['points'][player] += points_to_gain
                await send_clients_log_message(f"{player} leader is on a corner tile, {game_state['tiles'][tile_index_of_leader].name}, so gains {points_to_gain} points")