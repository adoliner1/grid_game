import game_utilities
import game_constants
from tiles.tile import Tile

class Ember(Tile):
    def __init__(self):
        super().__init__(
            name="Ember",
            type="Scorer",
            minimum_influence_to_rule=3,
            influence_tiers=[],
            description=f"You may not ((recruit)) here\nWhen a disciple is ^^burned^^, the owner [[receives]] a copy of it here\n\nAt the __end of each round__, if Ember is full, remove all the disciples. +6 points to whichever player had more",
            number_of_slots=9,
            disciples_which_can_be_recruited_to_this=[]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        burned_disciple = data.get('disciple')
        burned_color = data.get('color')

        await send_clients_log_message(f"**{self.name}** triggers")
        await game_utilities.player_receives_a_disciple_on_tile(
            game_state, 
            game_action_container_stack, 
            send_clients_log_message, 
            get_and_send_available_actions, 
            send_clients_game_state, 
            burned_color, 
            self, 
            burned_disciple
        )
    def modify_expected_incomes(self, game_state):
        if all(slot is not None for slot in self.slots_for_disciples):
            red_count = sum(1 for slot in self.slots_for_disciples if slot["color"] == "red")
            blue_count = sum(1 for slot in self.slots_for_disciples if slot["color"] == "blue")
            
            if red_count > blue_count:
                winner = "red"
            elif blue_count > red_count:
                winner = "blue"

            game_state["expected_points_incomes"][winner] += 6

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        if all(slot is not None for slot in self.slots_for_disciples):
            red_count = sum(1 for slot in self.slots_for_disciples if slot["color"] == "red")
            blue_count = sum(1 for slot in self.slots_for_disciples if slot["color"] == "blue")
            
            if red_count > blue_count:
                winner = "red"
            elif blue_count > red_count:
                winner = "blue"

            game_state["points"][winner] += 6
            await send_clients_log_message(f"Red had {red_count} disciples on ember, blue had {blue_count}. {winner} gains 6 points. **{self.name}** is emptied")

            self.slots_for_disciples = [None] * self.number_of_slots