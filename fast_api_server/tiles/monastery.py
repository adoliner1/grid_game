import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class Monastery(Tile):
    def __init__(self):
        super().__init__(
            name="Monastery",
            type="Giver/Disciple Mover",
            description="At the __end of each round__, for each acolyte you have here, [[receive]] 2 follower here.",
            number_of_slots=12,
            minimum_influence_to_rule=5,            
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "**Action:** Pay one power to move one of your disciples from Monastery to an adjacent tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,
                    "leader_must_be_present": True, 
                    "data_needed_for_use": ["disciple_to_move", "slot_to_move_disciple_to"],
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        user = game_action_container.whose_action
        monastery_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if current_piece_of_data_to_fill == "disciple_to_move":
            slots_with_disciples = [i for i, slot in enumerate(self.slots_for_disciples) if slot and slot["color"] == user]
            if slots_with_disciples:
                available_actions["select_a_slot_on_a_tile"] = {monastery_index: slots_with_disciples}
        elif current_piece_of_data_to_fill == "slot_to_move_disciple_to":
            slots_on_adjacent_tiles = {}
            for index, tile in enumerate(game_state["tiles"]):
                if game_utilities.determine_if_directly_adjacent(monastery_index, index):
                    slots_without_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if not slot]
                    if slots_without_disciples:
                        slots_on_adjacent_tiles[index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_on_adjacent_tiles

    def get_useable_tiers(self, game_state):
        current_player = game_state['whose_turn_is_it']
        current_players_influence_here = self.influence_per_player[current_player]
        useable_tiers = []

        if (current_players_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and
            self.leaders_here[current_player] and
            game_state["power"][current_player] >= 1 and
            any(slot and slot["color"] == current_player for slot in self.slots_for_disciples)):
                useable_tiers.append(0)

        return useable_tiers
    
    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        slot_index_to_move_from = game_action_container.required_data_for_action['disciple_to_move']['slot_index']
        slot_index_to_move_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['slot_index']
        tile_index_to_move_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['tile_index']
        monastery_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use")
            return False

        if not self.leaders_here[user]:
            await send_clients_log_message(f"Your leader must be present on **{self.name}** to use it")
            return False

        if game_state["power"][user] < 1:
            await send_clients_log_message(f"Not enough power to use **{self.name}**")
            return False

        if self.slots_for_disciples[slot_index_to_move_from] is None or self.slots_for_disciples[slot_index_to_move_from]["color"] != user:
            await send_clients_log_message(f"Invalid disciple selected to move from **{self.name}**")
            return False
        
        if game_state['tiles'][tile_index_to_move_to].slots_for_disciples[slot_index_to_move_to] is not None:
            await send_clients_log_message(f"Slot to move to isn't empty")
            return False 

        if not game_utilities.determine_if_directly_adjacent(monastery_index, tile_index_to_move_to):
            await send_clients_log_message(f"Selected tile is not adjacent to **{self.name}**")
            return False

        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, monastery_index, slot_index_to_move_from, tile_index_to_move_to, slot_index_to_move_to)
        
        game_state["power"][user] -= 1
        await send_clients_log_message(f"{user} paid 1 power to move a disciple from **{self.name}** to **{game_state['tiles'][tile_index_to_move_to].name}**")
        
        return True    

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        first_player = game_state["first_player"]
        second_player = game_utilities.get_other_player_color(first_player)

        await send_clients_log_message(f"Running end of round effect for **{self.name}**")
        for player in [first_player, second_player]:
            acolyte_count = sum(1 for slot in self.slots_for_disciples if slot and slot["color"] == player and slot["disciple"] == "acolyte")
            followers_to_receive = acolyte_count * 2
            for _ in range(followers_to_receive):
                await game_utilities.player_receives_a_disciple_on_tile(
                    game_state, game_action_container_stack, send_clients_log_message, 
                    get_and_send_available_actions, send_clients_game_state, 
                    player, self, 'follower'
                )
            if followers_to_receive > 0:
                await send_clients_log_message(f"{player} received {followers_to_receive} followers on **{self.name}**")    