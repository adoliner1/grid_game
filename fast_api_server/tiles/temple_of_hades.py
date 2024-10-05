import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class TempleOfHades(Tile):
    def __init__(self):
        super().__init__(
            name="Temple of Hades",
            type="Giver",
            description="At the __end of each round__, for each follower you have here, [[receive]] another follower here",
            number_of_slots=9,
            minimum_influence_to_rule=3,            
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** ^^Burn^^ 3 of your followers here (one at a time) to [[receive]] a sage here",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": [],
                },
            ]      
        )

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        number_of_followers_current_player_has_here = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "follower" and slot["color"] == whose_turn_is_it)
        ruler = self.determine_ruler(game_state)

        if number_of_followers_current_player_has_here >= 3 and ruler == whose_turn_is_it and self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier']:
            useable_tiers.append(0)

        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)
        first_player_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == first_player and slot["disciple"] == "follower")
        second_player_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == second_player and slot["disciple"] == "follower")

        for _ in range(first_player_count):
            await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, first_player, self, 'follower')

        for _ in range(second_player_count):
            await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, second_player, self, 'follower')

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        follower_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "follower" and slot["color"] == player)
        
        if follower_count < 3:
            await send_clients_log_message(f"Not enough followers to burn on **{self.name}**")
            return False
        
        await send_clients_log_message(f"**{self.name}** is used")
        followers_burned = 0
        for index, slot in enumerate(self.slots_for_disciples):
            if slot and slot["disciple"] == "follower" and slot["color"] == player:
                await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), index)
                followers_burned += 1
                if followers_burned == 3:
                    break

        if followers_burned < 3:
            await send_clients_log_message(f"Not enough followers were burned on **{self.name}**")
            return False
        
        await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, self, 'sage')
        return True