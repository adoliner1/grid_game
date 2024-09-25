import game_utilities
import game_constants
from tiles.tile import Tile

class Highway(Tile):
    def __init__(self):
        super().__init__(
            name="Highway",
            type="Mover",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "**Action:** ^^Burn^^ one of your disciples here and pay one power to move a disciple on a tile to another tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,       
                    "leader_must_be_present": False,              
                    "data_needed_for_use": ["slot_and_tile_to_burn_disciple_from", "slot_and_tile_to_move_disciple_from", "slot_and_tile_to_move_disciple_to"]
                },
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,                    
                    "description": "**Action:** Pay one power to move a disciple on a tile to another tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,          
                    "leader_must_be_present": False,           
                    "data_needed_for_use": ["slot_and_tile_to_move_disciple_from", "slot_and_tile_to_move_disciple_to"]
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        current_player = game_state['whose_turn_is_it']
        current_players_influence_here = self.influence_per_player[current_player]
        current_players_power = game_state['power'][current_player]
        useable_tiers = []

        if (current_players_influence_here >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]['is_on_cooldown'] and
            game_utilities.has_presence(self, current_player) and
            current_players_power > 0):
                useable_tiers.append(0)

        if (not self.influence_tiers[1]['is_on_cooldown'] and
            self.determine_ruler(game_state) == current_player and
            current_players_influence_here >= self.influence_tiers[1]['influence_to_reach_tier'] and
            current_players_power > 0):
                useable_tiers.append(1)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill_in_current_action = game_action_container.get_next_piece_of_data_to_fill()     

        if current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_burn_disciple_from":
            slots_that_can_be_burned_from = game_utilities.get_slots_with_a_disciple_of_player_color_at_tile_index(game_state, game_action_container.whose_action, game_action_container.required_data_for_action["index_of_tile_in_use"])
            available_actions["select_a_slot_on_a_tile"] = {game_action_container.required_data_for_action["index_of_tile_in_use"]: slots_that_can_be_burned_from}
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_disciple_from":
            slots_with_a_disciple = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_with_disciples = []
                for slot_index, slot in enumerate(tile.slots_for_disciples):
                    if slot:
                        slots_with_disciples.append(slot_index)
                if slots_with_disciples:
                    slots_with_a_disciple[index] = slots_with_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_with_a_disciple
        elif current_piece_of_data_to_fill_in_current_action == "slot_and_tile_to_move_disciple_to":
            slots_without_a_disciple = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_disciples = []
                for slot_index, slot in enumerate(tile.slots_for_disciples):
                    if not slot:
                        slots_without_disciples.append(slot_index)
                if slots_without_disciples:
                    slots_without_a_disciple[index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        users_power = game_state['power'][user]
        
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"Tried to use **{self.name}** but it's on cooldown")
            return False
        
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use")
            return False
        
        if users_power < 1:
            await send_clients_log_message(f"Not enough power to use **{self.name}**")
            return False            

        index_of_highway = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        index_of_tile_to_move_disciple_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['tile_index']
        slot_index_to_move_disciple_to = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_to']['slot_index']
        index_of_tile_to_move_disciple_to = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_to']['tile_index']
        slot_index_to_move_disciple_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['slot_index']

        if tier_index == 0:
            slot_index_to_burn_disciple_from = game_action_container.required_data_for_action['slot_and_tile_to_burn_disciple_from']['slot_index']

            if self.slots_for_disciples[slot_index_to_burn_disciple_from]["color"] != game_action_container.whose_action:
                await send_clients_log_message(f"Tried to use **{self.name}** but chose a disciple owned by opponent to burn")
                return False

        if tier_index == 1:

            if user != self.determine_ruler(game_state):
                if not self.slots_for_disciples[slot_index_to_burn_disciple_from]:
                    await send_clients_log_message(f"Tried to use **{self.name}** but not the ruler")
                    return False

        if game_state["tiles"][index_of_tile_to_move_disciple_from].slots_for_disciples[slot_index_to_move_disciple_from] is None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot with no disciple to move from {game_state['tiles'][index_of_tile_to_move_disciple_from].name}")
            return False

        if game_state["tiles"][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to] is not None:
            await send_clients_log_message(f"Tried to use **{self.name}** but chose a slot that is not empty to move to at {game_state['tiles'][index_of_tile_to_move_disciple_to].name}")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of **{self.name}**")

        if tier_index == 0:
            await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_highway, slot_index_to_burn_disciple_from)

        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_move_disciple_from, slot_index_to_move_disciple_from, index_of_tile_to_move_disciple_to, slot_index_to_move_disciple_to)

        disciple_moved = game_state['tiles'][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to]["disciple"]
        color_of_disciple_moved = game_state['tiles'][index_of_tile_to_move_disciple_to].slots_for_disciples[slot_index_to_move_disciple_to]["color"]
        await send_clients_log_message(f"{user} used **{self.name}** to move a {color_of_disciple_moved}_{disciple_moved} from {game_state['tiles'][index_of_tile_to_move_disciple_from].name} to {game_state['tiles'][index_of_tile_to_move_disciple_to].name}. They paid one power")
        game_state['power'][user] -= 1
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True