import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class RiverOfSouls(Tile):
    def __init__(self):
        super().__init__(
            name="River of Souls",
            type="Disciple Mover/Burner",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your disciples here to move a disciple from the tile your leader is on to any tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,       
                    "leader_must_be_present": False,              
                    "data_needed_for_use": ["disciple_to_burn", "disciple_to_move", "slot_to_move_disciple_to"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        current_player = game_state['whose_turn_is_it']
        current_players_influence_here = self.influence_per_player[current_player]
        useable_tiers = []

        if (current_players_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]['is_on_cooldown'] and
            game_utilities.count_all_disciples_for_color_on_tile(current_player, self) > 0):
                useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()     

        if current_piece_of_data_to_fill_in_current_action == "disciple_to_burn":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_disciple_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill_in_current_action == "disciple_to_move":
            leader_tile_index = game_utilities.get_tile_index_of_leader(game_state, game_action_container.whose_action)

            if leader_tile_index is not None:
                slots_with_disciples = [index for index, slot in enumerate(game_state["tiles"][leader_tile_index].slots_for_disciples) if slot and 
                                        not (game_action_container.required_data_for_action['disciple_to_burn']['tile_index'] == leader_tile_index and game_action_container.required_data_for_action['disciple_to_burn']['slot_index'] == index)]
                available_actions["select_a_slot_on_a_tile"] = {leader_tile_index: slots_with_disciples}
        elif current_piece_of_data_to_fill_in_current_action == "slot_to_move_disciple_to":
            slots_without_a_disciple = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if not slot]
                if slots_without_disciples:
                    slots_without_a_disciple[index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"Tried to use **{self.name}** but it's on cooldown")
            return False
        
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use")
            return False

        index_of_river = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_to_burn_disciple_from = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_tile_to_move_disciple_from = game_action_container.required_data_for_action['disciple_to_move']['tile_index']
        slot_index_to_move_disciple_from = game_action_container.required_data_for_action['disciple_to_move']['slot_index']
        index_of_tile_to_move_disciple_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['tile_index']
        slot_index_to_move_disciple_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['slot_index']

        if self.slots_for_disciples[slot_index_to_burn_disciple_from]["color"] != user:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple owned by opponent to burn")
            return False

        leader_tile_index = game_utilities.get_tile_index_of_leader(game_state, user)
        if index_of_tile_to_move_disciple_from != leader_tile_index:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple not on your leader's tile")
            return False

        if game_state["tiles"][index_of_tile_to_move_disciple_from].slots_for_disciples[slot_index_to_move_disciple_from] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to move from {game_state['tiles'][index_of_tile_to_move_disciple_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to] is not None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_disciple_to].name}")
            return False

        if index_of_river == index_of_tile_to_move_disciple_from and slot_index_to_burn_disciple_from == slot_index_to_move_disciple_from:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose the same disciple to burn and move")
            return False

        await send_clients_log_message(f"Using **{self.name}**")

        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_river, slot_index_to_burn_disciple_from)

        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_move_disciple_from, slot_index_to_move_disciple_from, index_of_tile_to_move_disciple_to, slot_index_to_move_disciple_to)

        disciple_moved = game_state['tiles'][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to]["disciple"]
        color_of_disciple_moved = game_state['tiles'][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to]["color"]
        await send_clients_log_message(f"{user} used **{self.name}** to move a {color_of_disciple_moved}_{disciple_moved} from {game_state['tiles'][index_of_tile_to_move_disciple_from].name} to {game_state['tiles'][index_of_tile_to_move_disciple_to].name}")

        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True