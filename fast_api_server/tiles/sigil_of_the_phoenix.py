import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SigilOfThePhoenix(Tile):
    def __init__(self):
        super().__init__(
            name="Sigil of the Phoenix",
            type="Giver",
            minimum_influence_to_rule=4,
            number_of_slots=4,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "**Reaction:** After one of your disciples is ^^burned^^, [[receive]] a disciple of the same type at the tile it was burned on",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,         
                    "leader_must_be_present": False,             
                    "data_needed_for_use": ['confirm_choice']
                },           
            ],
        )

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        available_actions["select_a_tier"] = {game_utilities.find_index_of_tile_by_name(game_state, self.name): [0]}

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        player_influence = self.influence_per_player[player]
        required_influence = self.influence_tiers[0]['influence_to_reach_tier']

        if ruler != player:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False

        if player_influence < required_influence:
            await send_clients_log_message(f"{player} does not have enough influence to use **{self.name}**")
            return False

        index_of_tile_burned_at = game_action_container.required_data_for_action['index_of_tile_burned_at']    
        disciple_type = game_action_container.required_data_for_action['disciple_type']

        # Receive the disciple
        await game_utilities.player_receives_a_disciple_on_tile(
            game_state, 
            game_action_container_stack, 
            send_clients_log_message, 
            get_and_send_available_actions, 
            send_clients_game_state, 
            player, 
            game_state['tiles'][index_of_tile_burned_at], 
            disciple_type
        )

        await send_clients_log_message(f"{player} used **{self.name}** to receive a {disciple_type} at {game_state['tiles'][index_of_tile_burned_at].name}")
        self.influence_tiers[0]['is_on_cooldown'] = True
        return True
            
    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        color_burned = game_action_container_stack[-1].data_from_event['color']
        index_of_tile_burned_at = game_action_container_stack[-1].data_from_event['index_of_tile_burned_at']
        disciple_type = game_action_container_stack[-1].data_from_event['disciple']
        await send_clients_log_message(f"{color_burned} may react with **{self.name}**")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "index_of_tile_burned_at": index_of_tile_burned_at,
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": 0,
                "confirm_choice": None,
                "disciple_type": disciple_type,
            },
            whose_action=color_burned,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await get_and_send_available_actions()
        await game_action_container_stack[-1].event.wait()

    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data): 
        color_burned = data.get('color')
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')
        ruler = self.determine_ruler(game_state)
        
        if not self.influence_tiers[0]['is_on_cooldown'] and self.influence_per_player[color_burned] >= self.influence_tiers[0]['influence_to_reach_tier'] and ruler == color_burned:
            reactions_by_player[color_burned].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = [0]