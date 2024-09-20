import game_utilities
import game_constants
from tiles.tile import Tile

class Nitrogen(Tile):
    def __init__(self):
        super().__init__(
            name="Nitrogen",
            type="Giver/Power-Creator",
            minimum_influence_to_rule=3,
            description="At the __end of a round__, for each sage you have here, [[receive]] a acolyte and a follower here",
            number_of_slots=11,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 0,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your sets here for +5 power",
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
        
        follower_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "follower" and slot["color"] == whose_turn_is_it)
        acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "acolyte" and slot["color"] == whose_turn_is_it)
        sage_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "sage" and slot["color"] == whose_turn_is_it)
        
        if follower_count >= 1 and acolyte_count >= 1 and sage_count >= 1:
            useable_tiers.append(0)

        return useable_tiers

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"{self.name} runs")

        for player in [first_player, second_player]:
            sage_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == player and slot["disciple"] == "sage")
            
            for _ in range(sage_count):
                await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, self, 'acolyte')
                await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player, self, 'follower')
            
    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        
        follower_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "follower" and slot["color"] == player)
        acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "acolyte" and slot["color"] == player)
        sage_count = sum(1 for slot in self.slots_for_disciples if slot and slot["disciple"] == "sage" and slot["color"] == player)
        
        if follower_count < 1 or acolyte_count < 1 or sage_count < 1:
            await send_clients_log_message(f"Not enough disciples to burn a set on {self.name}")
            return False
        
        await send_clients_log_message(f"{self.name} is used")
        nitrogen_tile_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        disciples_burned = {'follower': 0, 'acolyte': 0, 'sage': 0}
        for i, slot in enumerate(self.slots_for_disciples):
            if slot and slot["color"] == player and disciples_burned[slot["disciple"]] < 1:
                await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, nitrogen_tile_index, i)
                disciples_burned[slot["disciple"]] += 1
                if all(count == 1 for count in disciples_burned.values()):
                    break
        
        await send_clients_log_message(f"{player} burns a set on {self.name}")
        
        power_to_gain = 5
        game_state["power"][player] += power_to_gain
        await send_clients_log_message(f"{player} gains {power_to_gain} power from burning a set on {self.name}")

        return True