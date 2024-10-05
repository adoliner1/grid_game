import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class TacticiansStone(Tile):
    def __init__(self):
        super().__init__(
            name="Tactician's Stone",
            type="Attacker",
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,                    
                    "description": "**Reaction:** After you [[receive]] a disciple, you may ^^burn^^ any disciple at or adjacent to the tile you received it",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False, 
                    "data_needed_for_use": ['disciple_to_burn'],
                },        
            ],            
            number_of_slots=3,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        slots_with_a_burnable_disciple = {}
        index_of_tile_received_at = game_action_container.required_data_for_action.get('index_of_tile_received_at')
        if index_of_tile_received_at is not None:
            # Include the tile where the disciple was received
            slots_with_disciples = [i for i, slot in enumerate(game_state["tiles"][index_of_tile_received_at].slots_for_disciples) if slot]
            if slots_with_disciples:
                slots_with_a_burnable_disciple[index_of_tile_received_at] = slots_with_disciples
            
            # Include adjacent tiles
            for tile_index in game_utilities.get_adjacent_tile_indices(index_of_tile_received_at):
                slots_with_disciples = [i for i, slot in enumerate(game_state["tiles"][tile_index].slots_for_disciples) if slot]
                if slots_with_disciples:
                    slots_with_a_burnable_disciple[tile_index] = slots_with_disciples
        available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_disciple

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if self.influence_tiers[tier_index]["must_be_ruler"] and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier {tier_index} of **{self.name}**")
            return False

        if self.influence_per_player[player] < self.influence_tiers[tier_index]["influence_to_reach_tier"]:
            await send_clients_log_message(f"Not enough influence to use tier {tier_index} of **{self.name}**")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of **{self.name}** is on cooldown")
            return False

        slot_index_to_burn_disciple = game_action_container.required_data_for_action['disciple_to_burn']['slot_index']
        index_of_tile_to_burn_disciple = game_action_container.required_data_for_action['disciple_to_burn']['tile_index']
        index_of_tile_received_at = game_action_container.required_data_for_action['index_of_tile_received_at']

        if not (index_of_tile_to_burn_disciple == index_of_tile_received_at or 
                game_utilities.determine_if_directly_adjacent(index_of_tile_to_burn_disciple, index_of_tile_received_at)):
            await send_clients_log_message(f"Tried to react with **{self.name}** but chose a tile that is not the received at tile or adjacent to it")
            return False            

        if game_state["tiles"][index_of_tile_to_burn_disciple].slots_for_disciples[slot_index_to_burn_disciple] is None:
            await send_clients_log_message(f"Tried to react with **{self.name}** but there is no disciple to burn at {game_state['tiles'][index_of_tile_to_burn_disciple].name} at slot {slot_index_to_burn_disciple}")
            return False

        await send_clients_log_message(f"Reacting with tier {tier_index} of **{self.name}**")

        self.influence_tiers[tier_index]["is_on_cooldown"] = True    
        await game_utilities.burn_disciple_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_disciple, slot_index_to_burn_disciple)

        return True
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        receiver = game_action_container_stack[-1].data_from_event['receiver']
        index_of_tile_received_at = game_action_container_stack[-1].data_from_event['index_of_tile_received_at']
        await send_clients_log_message(f"{receiver} may react with **{self.name}**")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "disciple_to_burn": {},
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": tier_index,
                "index_of_tile_received_at": index_of_tile_received_at
            },
            whose_action=receiver,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await get_and_send_available_actions()
        await game_action_container_stack[-1].event.wait()

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        receiver = data.get('receiver')
        index_of_tile_received_at = data.get('index_of_tile_received_at')

        tiers_that_can_be_reacted_with = []
        ruler = self.determine_ruler(game_state)
        player_influence = self.influence_per_player[receiver]

        if not self.influence_tiers[0]["is_on_cooldown"] and player_influence >= self.influence_tiers[0]['influence_to_reach_tier'] and ruler == receiver:
            tiers_that_can_be_reacted_with.append(0)

        if tiers_that_can_be_reacted_with:
            reactions_by_player[receiver].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with