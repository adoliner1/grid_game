import game_utilities
import game_constants

class RoundBonus:
    def __init__(self, name, description, listener_type, bonus_type, allowed_rounds):
        self.name = name
        self.description = description
        self.listener_type = listener_type
        self.bonus_type = bonus_type
        self.allowed_rounds = allowed_rounds

    def setup(self, game_state):
        game_state["listeners"][self.listener_type][self.name] = self.run_effect

    def cleanup(self, game_state):
        del game_state["listeners"][self.listener_type][self.name]

    def serialize(self):
        return self.description

    def modify_expected_incomes(self, game_state):
        pass  # Base method, to be overridden by subclasses

class PointsPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Row",
            description = "12 points ruled-tile row",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds = [0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

        if red_complete_rows > 0:
            points_to_gain = 12*red_complete_rows
            game_state["expected_points_incomes"]["red"] += points_to_gain

        if blue_complete_rows > 0:
            points_to_gain = 12*blue_complete_rows
            game_state["expected_points_incomes"]["blue"] += points_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

        if red_complete_rows > 0:
            points_to_gain = 12*red_complete_rows
            game_state["points"]["red"] += points_to_gain
            await send_clients_log_message(f"Red gets {points_to_gain} points for round bonus")

        if blue_complete_rows > 0:
            points_to_gain = 12*blue_complete_rows
            game_state["points"]["blue"] += points_to_gain
            await send_clients_log_message(f"Blue gets {points_to_gain} points for round bonus") 

class PointsPerColumn(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Column",
            description = "12 points ruled-tile column",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds = [0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

        if red_complete_columns > 0:
            points_to_gain = 12 * red_complete_columns
            game_state["expected_points_incomes"]["red"] += points_to_gain

        if blue_complete_columns > 0:
            points_to_gain = 12 * blue_complete_columns
            game_state["expected_points_incomes"]["blue"] += points_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

        if red_complete_columns > 0:
            points_to_gain = 12 * red_complete_columns
            game_state["points"]["red"] += points_to_gain
            await send_clients_log_message(f"Red gets {points_to_gain} points for round bonus")

        if blue_complete_columns > 0:
            points_to_gain = 12 * blue_complete_columns
            game_state["points"]["blue"] += points_to_gain
            await send_clients_log_message(f"Blue gets {points_to_gain} points for round bonus")

class PointsPerTileRuled(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "tile-rule points",
            description = "2 points ruled-tile",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        red_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "red")
        blue_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "blue")

        game_state["expected_points_incomes"]["red"] += 2 * red_tiles_ruled
        game_state["expected_points_incomes"]["blue"] += 2 * blue_tiles_ruled

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

class PowerPerPresence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Power for Presence",
            description= "power presence",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.update_presence(game_state)
        for player in ["red", "blue"]:
            presence = game_state["presence"][player]
            power_to_gain = presence
            game_state["expected_power_incomes"][player] += power_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            power_to_gain = presence
            game_state['power'][player] += power_to_gain
            await send_clients_log_message(f"{player} has {presence} presence and gains {power_to_gain} power")

class PowerPerPeakInfluence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Power for Peak-Influence",
            description="1/2 power peak-influence",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.determine_influence_levels(game_state)
        for player in ["red", "blue"]:
            peak_influence = game_state["peak_influence"][player]
            power_to_gain = peak_influence // 2
            game_state["expected_power_incomes"][player] += power_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_influence_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            peak_influence = game_state["peak_influence"][player]
            power_to_gain = peak_influence // 2
            game_state['power'][player] += power_to_gain
            await send_clients_log_message(f"{player} has a peak influence of {peak_influence} and gains {power_to_gain}")
            
class PowerForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Gain Power for Longest Chain",
            description="2 power ruled-tile longest-chain",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[]
        )

    def modify_expected_incomes(self, game_state):
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        for player in ["red", "blue"]:
            size_of_longest_chain = longest_chains[player]
            power_to_gain = size_of_longest_chain * 2
            game_state["expected_power_incomes"][player] += power_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        
        for player in [first_player, second_player]:
            player_color = "red" if player == "red" else "blue"
            size_of_longest_chain = longest_chains[player_color]
            power_to_gain = size_of_longest_chain*2
            game_state['power'][player] += power_to_gain
            await send_clients_log_message(f"{player} has a chain of size of {size_of_longest_chain} and gains {power_to_gain}")

class PointsForLongestChain(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Produce Points for Longest Chain",
            description="3 points ruled-tile longest-chain",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[]
        )

    def modify_expected_incomes(self, game_state):
        longest_chains = game_utilities.find_longest_chain_of_ruled_tiles(game_state['tiles'])
        for player in ["red", "blue"]:
            points_to_award = longest_chains[player] * 3
            game_state["expected_points_incomes"][player] += points_to_award

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
            description="points presence",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[0,1,2,3]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.update_presence(game_state)
        for player in ["red", "blue"]:
            presence = game_state["presence"][player]
            points_to_award = presence
            game_state["expected_points_incomes"][player] += points_to_award

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            points_to_award = presence
            
            game_state["points"][player] += points_to_award
            await send_clients_log_message(f"{player} gains {points_to_award} points from {self.name} (presence: {presence})")

class PointsPerPeakInfluence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for Peak Influence",
            description="1/2 points peak-influence",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[0,1,2,3]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.determine_influence_levels(game_state)
        for player in ["red", "blue"]:
            peak_influence = game_state["peak_influence"][player]
            points_to_award = peak_influence // 2
            game_state["expected_points_incomes"][player] += points_to_award

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_influence_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            peak_influence = game_state["peak_influence"][player]
            points_to_award = peak_influence // 2
            
            game_state["points"][player] += points_to_award
            await send_clients_log_message(f"{player} gains {points_to_award} points from {self.name} (peak influence: {peak_influence})")

class PowerForCorner(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Power for Corner",
            description="3 power ruled-tile corner",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        for player in ["red", "blue"]:
            corner_tiles_ruled = sum(1 for tile_index in game_constants.corner_tiles 
                                     if game_state["tiles"][tile_index].determine_ruler(game_state) == player)
            game_state["expected_power_incomes"][player] += 3 * corner_tiles_ruled

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
       
        for player in [first_player, second_player]:
            corner_tiles_ruled = 0
            for tile_index in game_constants.corner_tiles:
                if game_state["tiles"][tile_index].determine_ruler(game_state) == player:
                    corner_tiles_ruled += 1
            
            if corner_tiles_ruled > 0:
                power_to_gain = 3 * corner_tiles_ruled
                game_state['power'][player] += power_to_gain
                corner_names = ", ".join(game_state['tiles'][tile_index].name for tile_index in game_constants.corner_tiles 
                                         if game_state["tiles"][tile_index].determine_ruler(game_state) == player)
                await send_clients_log_message(f"{player} rules {corner_tiles_ruled} corner tile{'s' if corner_tiles_ruled > 1 else ''} ({corner_names}), so gains {power_to_gain} power")

class PowerPerRow(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Power Per Completed Row",
            description = "7 power ruled-tile row",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[]
        )

    def modify_expected_incomes(self, game_state):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

        game_state["expected_power_incomes"]["red"] += 7 * red_complete_rows
        game_state["expected_power_incomes"]["blue"] += 7 * blue_complete_rows

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "red")
        blue_complete_rows = game_utilities.determine_how_many_full_rows_player_rules(game_state, "blue")

        for player, complete_rows in [("red", red_complete_rows), ("blue", blue_complete_rows)]:
            if complete_rows > 0:
                power_to_gain = 7 * complete_rows
                game_state["power"][player] += power_to_gain
                await send_clients_log_message(f"{player} gains {power_to_gain} power for {complete_rows} completed row(s)")

class PowerPerColumn(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Power Per Completed Column",
            description = "7 power ruled-tile column",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[]
        )

    def modify_expected_incomes(self, game_state):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

        game_state["expected_power_incomes"]["red"] += 7 * red_complete_columns
        game_state["expected_power_incomes"]["blue"] += 7 * blue_complete_columns

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "red")
        blue_complete_columns = game_utilities.determine_how_many_full_columns_player_rules(game_state, "blue")

        for player, complete_columns in [("red", red_complete_columns), ("blue", blue_complete_columns)]:
            if complete_columns > 0:
                power_to_gain = 7 * complete_columns
                game_state["power"][player] += power_to_gain
                await send_clients_log_message(f"{player} gains {power_to_gain} power for {complete_columns} completed column(s)")

class PowerPerTileRuled(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Power Per Tile Ruled",
            description = "2 power ruled-tile",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        red_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "red")
        blue_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "blue")

        game_state["expected_power_incomes"]["red"] += red_tiles_ruled*2
        game_state["expected_power_incomes"]["blue"] += blue_tiles_ruled*2

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "red")
        blue_tiles_ruled = sum(1 for tile in game_state["tiles"] if tile.ruler == "blue")

        for player, tiles_ruled in [("red", red_tiles_ruled), ("blue", blue_tiles_ruled)]:
            if tiles_ruled > 0:
                power_to_gain = tiles_ruled*2
                game_state["power"][player] += power_to_gain
                await send_clients_log_message(f"{player} gains {power_to_gain} power for ruling {tiles_ruled} tile(s)")

class PointsForCorner(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for Corner",
            description="5 points ruled-tile corner",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        for player in ["red", "blue"]:
            corner_tiles_ruled = sum(1 for tile_index in game_constants.corner_tiles 
                                     if game_state["tiles"][tile_index].determine_ruler(game_state) == player)
            game_state["expected_points_incomes"][player] += 5 * corner_tiles_ruled

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
       
        for player in [first_player, second_player]:
            corner_tiles_ruled = 0
            ruled_corner_names = []
            for tile_index in game_constants.corner_tiles:
                if game_state["tiles"][tile_index].determine_ruler(game_state) == player:
                    corner_tiles_ruled += 1
                    ruled_corner_names.append(game_state['tiles'][tile_index].name)
            
            if corner_tiles_ruled > 0:
                points_to_gain = 5 * corner_tiles_ruled
                game_state['points'][player] += points_to_gain
                corner_names = ", ".join(ruled_corner_names)
                await send_clients_log_message(f"{player} rules {corner_tiles_ruled} corner tile{'s' if corner_tiles_ruled > 1 else ''} ({corner_names}), so gains {points_to_gain} points")

class PowerPerDiagonal(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Power Per Completed Diagonal",
            description = "10 power ruled-tile diagonal",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[]
        )
    
    def modify_expected_incomes(self, game_state):
        red_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "red")
        blue_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "blue")
        game_state["expected_power_incomes"]["red"] += 10 * red_complete_diagonals
        game_state["expected_power_incomes"]["blue"] += 10 * blue_complete_diagonals
    
    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "red")
        blue_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "blue")
        for player, complete_diagonals in [("red", red_complete_diagonals), ("blue", blue_complete_diagonals)]:
            if complete_diagonals > 0:
                power_to_gain = 10 * complete_diagonals
                game_state["power"][player] += power_to_gain
                await send_clients_log_message(f"{player} gains {power_to_gain} power for {complete_diagonals} completed diagonal(s)")

class PointsPerDiagonal(RoundBonus):
    def __init__(self):
        super().__init__(
            name = "Points Per Completed Diagonal",
            description = "16 points ruled-tile diagonal",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds = [3,4,5]
        )
    
    def modify_expected_incomes(self, game_state):
        red_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "red")
        blue_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "blue")
        if red_complete_diagonals > 0:
            points_to_gain = 16 * red_complete_diagonals
            game_state["expected_points_incomes"]["red"] += points_to_gain
        if blue_complete_diagonals > 0:
            points_to_gain = 16 * blue_complete_diagonals
            game_state["expected_points_incomes"]["blue"] += points_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        red_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "red")
        blue_complete_diagonals = game_utilities.determine_how_many_full_diagonals_player_rules(game_state, "blue")
        if red_complete_diagonals > 0:
            points_to_gain = 16 * red_complete_diagonals
            game_state["points"]["red"] += points_to_gain
        if blue_complete_diagonals > 0:
            points_to_gain = 16 * blue_complete_diagonals
            game_state["points"]["blue"] += points_to_gain

class PointsForAllCorners(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Points for All Corners Ruled",
            description="25 points ruled-tile corner",
            listener_type="end_of_round",
            bonus_type="scorer",
            allowed_rounds=[5]
        )

    def modify_expected_incomes(self, game_state):
        for player in ["red", "blue"]:
            if all(game_state["tiles"][corner].ruler == player for corner in game_constants.corner_tiles):
                game_state["expected_points_incomes"][player] += 25

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
        
        for player in [first_player, second_player]:
            if all(game_state["tiles"][corner].ruler == player for corner in game_constants.corner_tiles):
                points_to_gain = 25
                game_state['points'][player] += points_to_gain
                await send_clients_log_message(f"{player} rules all 4 corner tiles and gains {points_to_gain} points")

class LeaderMovementForPresence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Leader Movement for Presence",
            description="1/2 leader-movement presence",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.update_presence(game_state)
        for player in ["red", "blue"]:
            presence = game_state["presence"][player]
            movement_to_gain = presence // 2
            game_state["expected_leader_movement_incomes"][player] += movement_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.update_presence(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            presence = game_state["presence"][player]
            movement_to_gain = presence // 2
            game_state['leader_movement'][player] += movement_to_gain
            await send_clients_log_message(f"{player} has {presence} presence and gains {movement_to_gain} leader_movement")

class LeaderMovementForPeakInfluence(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Leader Movement for Peak Influence",
            description="1/3 leader-movement peak-influence",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        game_utilities.determine_influence_levels(game_state)
        for player in ["red", "blue"]:
            peak_influence = game_state["peak_influence"][player]
            movement_to_gain = peak_influence // 3
            game_state["expected_leader_movement_incomes"][player] += movement_to_gain

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        game_utilities.determine_influence_levels(game_state)
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)

        for player in [first_player, second_player]:
            peak_influence = game_state["peak_influence"][player]
            movement_to_gain = peak_influence // 3
            game_state['leader_movement'][player] += movement_to_gain
            await send_clients_log_message(f"{player} has a peak influence of {peak_influence} and gains {movement_to_gain} leader_movement")

class LeaderMovementForCorner(RoundBonus):
    def __init__(self):
        super().__init__(
            name="Leader Movement for Corner",
            description="2 leader-movement ruled-tile corner",
            listener_type="end_of_round",
            bonus_type="income",
            allowed_rounds=[0,1,2,3,4,5]
        )

    def modify_expected_incomes(self, game_state):
        for player in ["red", "blue"]:
            corner_tiles_ruled = sum(1 for tile_index in game_constants.corner_tiles 
                                     if game_state["tiles"][tile_index].determine_ruler(game_state) == player)
            game_state["expected_leader_movement_incomes"][player] += 2 * corner_tiles_ruled

    async def run_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, **data):
        first_player = game_state['first_player']
        second_player = game_utilities.get_other_player_color(first_player)
       
        for player in [first_player, second_player]:
            corner_tiles_ruled = 0
            ruled_corner_names = []
            for tile_index in game_constants.corner_tiles:
                if game_state["tiles"][tile_index].determine_ruler(game_state) == player:
                    corner_tiles_ruled += 1
                    ruled_corner_names.append(game_state['tiles'][tile_index].name)
            
            if corner_tiles_ruled > 0:
                movement_to_gain = 2 * corner_tiles_ruled
                game_state['leader_movement'][player] += movement_to_gain
                corner_names = ", ".join(ruled_corner_names)
                await send_clients_log_message(f"{player} rules {corner_tiles_ruled} corner tile{'s' if corner_tiles_ruled > 1 else ''} ({corner_names}), so gains {movement_to_gain} leader_movement")