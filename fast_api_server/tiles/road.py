import game_utilities
import game_constants
from tiles.tile import Tile

class Road(Tile):
    def __init__(self):
        super().__init__(
            name="Road",
            type="Mover",
            minimum_influence_to_rule=5,
            number_of_slots=7,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": False,
                    "description": "**Action:** Choose a disciple at an adjacent tile. Move it anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,     
                    "leader_must_be_present": False,                
                    "data_needed_for_use": ["slot_and_tile_to_move_disciple_from", "slot_and_tile_to_move_disciple_to"]
                },
                {
                    "influence_to_reach_tier": 8,
                    "must_be_ruler": True,
                    "description": "**Action:** Same as above but choose any disciple",
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
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        player_influence = self.influence_per_player[whose_turn_is_it]

        for i, tier in enumerate(self.influence_tiers):
            if player_influence >= tier["influence_to_reach_tier"] and not tier["is_on_cooldown"]:
                useable_tiers.append(i)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        current_piece_of_data_to_fill = game_action_container.get_next_piece_of_data_to_fill()
        if current_piece_of_data_to_fill == "slot_and_tile_to_move_disciple_from":
            slots_with_a_disciple = {}
            index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            user = game_action_container.whose_action

            if tier_index == 2:
                for index, tile in enumerate(game_state["tiles"]):
                    slots_with_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if slot]
                    if slots_with_disciples:
                        slots_with_a_disciple[index] = slots_with_disciples
            else:
                adjacent_tiles = game_utilities.get_adjacent_tile_indices(index_of_road)
                for index in adjacent_tiles:
                    slots_with_disciples = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_disciples) if slot]
                    if slots_with_disciples:
                        slots_with_a_disciple[index] = slots_with_disciples

            available_actions["select_a_slot_on_a_tile"] = slots_with_a_disciple
        elif current_piece_of_data_to_fill == "slot_and_tile_to_move_disciple_to":
            slots_without_a_disciple_per_tile = {}
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_disciples = [i for i, slot in enumerate(tile.slots_for_disciples) if not slot]
                if slots_without_disciples:
                    slots_without_a_disciple_per_tile[index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple_per_tile

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        user_influence = self.influence_per_player[user]

        if user_influence < self.influence_tiers[tier_index]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use tier {tier_index} of {self.name}")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False

        index_of_road = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['slot_index']
        tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['tile_index']
        slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_to']['tile_index']

        if tier_index == 0 and not game_utilities.determine_if_directly_adjacent(index_of_road, tile_index_from):
            await send_clients_log_message(f"Tried to use {self.name} but chose a non-adjacent tile")
            return False

        if game_state["tiles"][tile_index_from].slots_for_disciples[slot_index_from] is None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot with no disciple to move from {game_state['tiles'][tile_index_from].name}")
            return False

        if game_state["tiles"][tile_index_to].slots_for_disciples[slot_index_to] is not None:
            await send_clients_log_message(f"Tried to use {self.name} but chose a slot that is not empty to move to at {game_state['tiles'][tile_index_to].name}")
            return False

        await send_clients_log_message(f"Using tier {tier_index} of {self.name}")
        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        
        self.influence_tiers[tier_index]["is_on_cooldown"] = True 
        return True