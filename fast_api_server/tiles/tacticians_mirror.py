import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class TacticiansMirror(Tile):
    def __init__(self):
        super().__init__(
            name="Tactician's Mirror",
            type="Disciple Mover",
            minimum_influence_to_rule=3,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": True,
                    "description": "**Reaction:** After you [[receive]] a disciple, you may move it to a tile adjacent to the tile you [[received]] it at",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,  
                    "leader_must_be_present": False,
                    "data_needed_for_use": ['slot_to_move_disciple_to']
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        index_of_tile_received_at = game_action_container.required_data_for_action.get('slot_and_tile_to_move_disciple_from', {}).get('tile_index')
        if index_of_tile_received_at is not None:
            adjacent_tiles = game_utilities.get_adjacent_tile_indices(index_of_tile_received_at)
            slots_without_a_disciple_per_tile = {}
            for index in adjacent_tiles:
                slots_without_disciples = [i for i, slot in enumerate(game_state["tiles"][index].slots_for_disciples) if not slot]
                if slots_without_disciples:
                    slots_without_a_disciple_per_tile[index] = slots_without_disciples
            available_actions["select_a_slot_on_a_tile"] = slots_without_a_disciple_per_tile

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_per_player[game_action_container.whose_action] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Cannot react with tier {tier_index} of **{self.name}**, not enough influence")
            return False
        
        if self.influence_tiers[tier_index]["must_be_ruler"] and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier **{self.name}**")
            return False

        slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['slot_index']
        tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_disciple_from']['tile_index']
        slot_index_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['slot_index']
        tile_index_to = game_action_container.required_data_for_action['slot_to_move_disciple_to']['tile_index']

        if not game_utilities.determine_if_directly_adjacent(tile_index_from, tile_index_to):
            await send_clients_log_message(f"Tried to react with **{self.name}** but destination tile isn't adjacent to the tile where the disciple was received")
            return False

        if game_state["tiles"][tile_index_from].slots_for_disciples[slot_index_from] is None:
            await send_clients_log_message(f"Tried to react with **{self.name}** but there is no disciple to move")
            return False

        if game_state["tiles"][tile_index_to].slots_for_disciples[slot_index_to] is not None:
            await send_clients_log_message(f"Tried to react with **{self.name}** but chose a non-empty slot to move to")
            return False

        await send_clients_log_message(f"Reacting with tier {tier_index} of **{self.name}**")
        await game_utilities.move_disciple_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        
        return True

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        receiver = game_action_container_stack[-1].data_from_event['receiver']
        index_of_slot_received_at = game_action_container_stack[-1].data_from_event['index_of_slot_received_at']
        index_of_tile_received_at = game_action_container_stack[-1].data_from_event['index_of_tile_received_at']
        await send_clients_log_message(f"{receiver} may react with **{self.name}**")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "slot_and_tile_to_move_disciple_from": {"slot_index": index_of_slot_received_at, "tile_index": index_of_tile_received_at},
                "slot_to_move_disciple_to": {},
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": tier_index
            },
            whose_action=receiver,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await get_and_send_available_actions()
        await game_action_container_stack[-1].event.wait()

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        receiver = data.get('receiver')
        tiers_that_can_be_reacted_with = []
        
        if not self.influence_tiers[0]['is_on_cooldown'] and self.influence_per_player[receiver] >= self.influence_tiers[0]['influence_to_reach_tier']:
            tiers_that_can_be_reacted_with.append(0)
        
        if tiers_that_can_be_reacted_with:
            reactions_by_player[receiver].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with