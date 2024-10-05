import game_utilities
import game_constants
from tiles.tile import Tile

class EternalLattice(Tile):
    def __init__(self):
        super().__init__(
            name="Eternal Lattice",
            type="Generator",
            minimum_influence_to_rule=3,
            description="At the __end of each round__, for each unique pair you have here, +1 power\nIf you have all three possible pairs, +6 power per pair instead",
            number_of_slots=8,
            influence_tiers=[],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def modify_expected_incomes(self, game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
       
        for color in [first_player, second_player]:
            disciple_counts = {"follower": 0, "acolyte": 0, "sage": 0}
            for slot in self.slots_for_disciples:
                if slot and slot["color"] == color:
                    disciple_counts[slot["disciple"]] += 1
           
            power_gained = 0
            for disciple, count in disciple_counts.items():
                if count >= 2:
                    power_gained += 1
           
            # If it's 3, they have all 3 possible pairs
            if power_gained == 3:
                power_gained = 18
            
            if power_gained > 0:
                game_state["expected_power_incomes"][color] += power_gained

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        
        for color in [first_player, second_player]:
            disciple_counts = {"follower": 0, "acolyte": 0, "sage": 0}
            for slot in self.slots_for_disciples:
                if slot and slot["color"] == color:
                    disciple_counts[slot["disciple"]] += 1
            
            power_gained = 0
            for disciple, count in disciple_counts.items():
                if count >= 2:
                    power_gained += 1
            
            #if it's 3, they have all 3 possible pairs
            if power_gained == 3:
                await send_clients_log_message(f"{color} has all three possible pairs at **{self.name}**")
                power_gained = 18

            if power_gained > 0:
                game_state["power"][color] += power_gained
                await send_clients_log_message(f"{color} gains {power_gained} power from **{self.name}**")