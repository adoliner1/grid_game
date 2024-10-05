from .tile import Tile
from .. import game_utilities
from .. import game_constants

class Monastery(Tile):
    def __init__(self):
        super().__init__(
            name="Monastery",
            type="Giver/Disciple Mover",
            description = "At the __end of each round__, for each acolyte you have here, [[receive]] a follower here.",
            number_of_slots=4,
            minimum_influence_to_rule=4,            
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,                    
                    "description": "**Action:** If Monastery is full, move one of your followers from Monastery anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": ["slot_to_move_follower_to"],
                },
            ]     
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        slots_without_a_disciple = {}
        for index, tile in enumerate(game_state["tiles"]):
            slots_without_disciples = []
            for slot_index, slot in enumerate(tile.slots_for_disciples):
                if not slot:
                    slots_without_disciples.append(slot_index)
            if slots_without_disciples:
                slots_without_a_disciple[index] = slots_without_disciples
        available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple

    def get_useable_tiers(self, game_state):
        current_player = game_state['whose_turn_is_it']
        current_players_influence_here = self.influence_per_player[current_player]
        useable_tiers = []

        if (current_players_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and
            self.determine_ruler(game_state) == current_player and
            None not in self.slots_for_disciples and
            any(slot and slot["disciple"] == "follower" and slot["color"] == current_player for slot in self.slots_for_disciples) and 
            not self.influence_tiers[0]['is_on_cooldown']):
                useable_tiers.append(0)

        return useable_tiers
    
    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        slot_index_to_move_follower_to = game_action_container.required_data_for_action['slot_to_move_follower_to']['slot_index']
        tile_index_to_move_follower_to = game_action_container.required_data_for_action['slot_to_move_follower_to']['tile_index']
        tile_to_move_follower_to = game_state['tiles'][tile_index_to_move_follower_to]
        index_of_boron = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use")
            return False

        if None in self.slots_for_disciples:
            await send_clients_log_message(f"**{self.name}** isn't full and can't be used")
            return False
        
        if self.influence_tiers[tier_index]['influence_to_reach_tier']['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False
        
        slot_index_to_move_follower_from = None
        for index, slot in enumerate(self.slots_for_disciples):
            if slot and slot["disciple"] == "follower" and slot["color"] == user:
                slot_index_to_move_follower_from = index

        if slot_index_to_move_follower_from == None:
            await send_clients_log_message(f"No {user}_follower on **{self.name}** to move")
            return False
        
        if tile_to_move_follower_to.slots_for_disciples[slot_index_to_move_follower_to] is not None:
            await send_clients_log_message(f"Slot to move to isn't empty")
            return False 
        
        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_boron, slot_index_to_move_follower_from, tile_index_to_move_follower_to, slot_index_to_move_follower_to)
        return True    

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Running end of round effect for **{self.name}**")
        for player in [first_player, second_player]:
            acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == player and slot["disciple"] == "acolyte")
            for _ in range(acolyte_count):
                await game_utilities.player_receives_a_disciple_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    get_and_send_available_actions, send_clients_game_state, 
                    player, self, 'follower'
                )

    