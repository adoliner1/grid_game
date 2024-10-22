import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SolariumOfTheTactician(Tile):
    def __init__(self):
        super().__init__(
            name="Solarium of the Tactician",
            type="Tile-Mover",
            number_of_slots=3,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Reaction:** After you [[receive]] a disciple, at or adjacent to Solarium of the Tactician, swap it with an adjacent tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,        
                    "leader_must_be_present": False,            
                    "data_needed_for_use": ['tile_to_swap_with']
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        
        solarium_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        adjacent_tiles = game_utilities.get_adjacent_tile_indices(solarium_index)
        available_actions["select_a_tile"] = adjacent_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Cannot react with **{self.name}**, not enough influence")
            return False

        if user != ruler:
            await send_clients_log_message(f"Only the ruler can react with **{self.name}**")
            return False

        tile_to_swap_with = game_action_container.required_data_for_action["tile_to_swap_with"]
        solarium_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if tile_to_swap_with is None:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False
        
        if not game_utilities.determine_if_directly_adjacent(solarium_index, tile_to_swap_with):
            await send_clients_log_message(f"Can only swap with adjacent tiles using **{self.name}**")
            return False

        await send_clients_log_message(f"Reacted with **{self.name}** to swap with **{game_state['tiles'][tile_to_swap_with].name}**")
        
        # Swap the tiles
        game_state["tiles"][solarium_index], game_state["tiles"][tile_to_swap_with] = game_state["tiles"][tile_to_swap_with], game_state["tiles"][solarium_index]
        
        return True

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        receiver = game_action_container_stack[-1].data_from_event['receiver']
        await send_clients_log_message(f"{receiver} may react with **{self.name}**")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": tier_index,
                "tile_to_swap_with": None
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
        solarium_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if not (index_of_tile_received_at == solarium_index or 
                game_utilities.determine_if_directly_adjacent(solarium_index, index_of_tile_received_at)):
            return
            
        tiers_that_can_be_reacted_with = []
        
        if (not self.influence_tiers[0]['is_on_cooldown'] and 
            self.influence_per_player[receiver] >= self.influence_tiers[0]['influence_to_reach_tier']):
            tiers_that_can_be_reacted_with.append(0)
        
        if tiers_that_can_be_reacted_with:
            reactions_by_player[receiver].tiers_to_resolve[solarium_index] = tiers_that_can_be_reacted_with