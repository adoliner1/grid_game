import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class UnholyAtheneum(Tile):
    def __init__(self):
        super().__init__(
            name="Unholy Atheneum",
            type="Giver/Generator",
            description="At the __end of each round__, for each sage you have here, [[receive]] an acolyte then a follower here",
            number_of_slots=10,
            minimum_influence_to_rule=7,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "**Action:** If Unholy Atheneum is full, you may ^^burn^^ one of your disciples here to gain power equal to its recruitment cost + 1",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False,                      
                    "data_needed_for_use": ['disciple_to_burn'],
                },            
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        slots_with_burnable_disciples = []
        current_player = game_state['whose_turn_is_it']
        index_of_unholy_atheneum = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        for slot_index, slot in enumerate(self.slots_for_disciples):
            if slot and slot["color"] == current_player:
                slots_with_burnable_disciples.append(slot_index)
        available_actions["select_a_slot_on_a_tile"] = {index_of_unholy_atheneum: slots_with_burnable_disciples}

    def get_useable_tiers(self, game_state):
        current_player = game_state['whose_turn_is_it']
        current_players_influence_here = self.influence_per_player[current_player]
        useable_tiers = []

        if (current_players_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and
            self.determine_ruler(game_state) == current_player and
            None not in self.slots_for_disciples and
            any(slot and slot["color"] == current_player for slot in self.slots_for_disciples) and 
            not self.influence_tiers[0]['is_on_cooldown']):
                useable_tiers.append(0)

        return useable_tiers
    
    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        slot_index_to_burn_disciple = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_unholy_atheneum = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use")
            return False

        if None in self.slots_for_disciples:
            await send_clients_log_message(f"**{self.name}** isn't full and can't be used")
            return False
        
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        if self.slots_for_disciples[slot_index_to_burn_disciple] is None or self.slots_for_disciples[slot_index_to_burn_disciple]["color"] != user:
            await send_clients_log_message(f"No {user} disciple at the selected slot on **{self.name}** to burn")
            return False
        
        disciple_type = self.slots_for_disciples[slot_index_to_burn_disciple]["disciple"]
        power_to_gain = game_state['recruiting_costs'][user][disciple_type] + 1
        
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_unholy_atheneum, slot_index_to_burn_disciple)
        
        game_state["power"][user] += power_to_gain
        await send_clients_log_message(f"{user} gains {power_to_gain} power from burning a {disciple_type} on **{self.name}**")

        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True    

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Running end of round effect for **{self.name}**")
        for player in [first_player, second_player]:
            sage_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == player and slot["disciple"] == "sage")
            for _ in range(sage_count):
                await game_utilities.player_receives_a_disciple_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    get_and_send_available_actions, send_clients_game_state, 
                    player, self, 'acolyte'
                )
                await game_utilities.player_receives_a_disciple_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    get_and_send_available_actions, send_clients_game_state, 
                    player, self, 'follower'
                )