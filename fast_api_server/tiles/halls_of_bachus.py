import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class HallsOfBacchus(Tile):
    def __init__(self):
        super().__init__(
            name="Halls of Bacchus",
            type="Giver/Generator",
            minimum_influence_to_rule=4,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "If the Halls of Bacchus are full, +3 power at the __end of each round__",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                    "leader_must_be_present": False,
                    "data_needed_for_use": []
                },
            ],
            description=f"You may not ((recruit)) here\n\nWhen a disciple is ^^burned^^, the owner [[receives]] a copy of it here",
            number_of_slots=6,
            disciples_which_can_be_recruited_to_this=[],
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
        ruler = self.determine_ruler(game_state)
        if ruler and all(slot is not None for slot in self.slots_for_disciples):
            game_state["expected_power_incomes"][ruler] += 3

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler and all(slot is not None for slot in self.slots_for_disciples):
            game_state["power"][ruler] += 3
            await send_clients_log_message(f"**{self.name}** is full. The ruler, {ruler}, gains 3 power.")
