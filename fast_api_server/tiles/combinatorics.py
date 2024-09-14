import game_utilities
import game_constants
from tiles.tile import Tile

class Combinatorics(Tile):
    def __init__(self):
        super().__init__(
            name="Combinatorics",
            type="Producer/Scorer",
            minimum_power_to_rule=3,
            description="At the __end of a round__, for each unique, same-shape pair you have here, +1 stamina\nIf you have a triangle here, +2 points per stamina you gained this way",
            number_of_slots=9,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        
        for color in [first_player, second_player]:
            shape_counts = {"circle": 0, "square": 0, "triangle": 0}
            for slot in self.slots_for_shapes:
                if slot and slot["color"] == color:
                    shape_counts[slot["shape"]] += 1
            
            stamina_gained = 0
            for shape, count in shape_counts.items():
                if count >= 2:
                    stamina_gained += 1
            
            if stamina_gained > 0:
                game_state["stamina"][color] += stamina_gained
                await send_clients_log_message(f"{color} gains {stamina_gained} stamina from {self.name}")
            
            if shape_counts["triangle"] > 0:
                bonus_points = stamina_gained * 2
                game_state["points"][color] += bonus_points
                await send_clients_log_message(f"{color} gains {bonus_points} points from {self.name} (2 points per {stamina_gained} stamina gained)")