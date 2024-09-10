import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Plains(Tile):
    def __init__(self):
        super().__init__(
            name="Plains",
            type="Producer/Scorer",
            minimum_power_to_rule=3,
            number_of_slots=7,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "When a tile ++produces++ a shape, you may [[receive]] a circle at a tile adjacent to it",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": ['tile_to_receive_shape']
                },
                {
                    "power_to_reach_tier": 6,
                    "must_be_ruler": False,                    
                    "description": "Same as above but [[receive]] a square instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": ['tile_to_receive_shape']
                },
                {
                    "power_to_reach_tier": 9,
                    "must_be_ruler": True,                    
                    "description": "Same as above but [[receive]] a triangle instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": ['tile_to_receive_shape']
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        producing_tile_index = game_action_container.required_data_for_action.get('producing_tile_index')
        if producing_tile_index is not None:
            adjacent_tiles = game_utilities.get_adjacent_tile_indices(producing_tile_index)
            plains_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            available_tiles = [tile_index for tile_index in adjacent_tiles if tile_index != plains_index]
            available_actions["select_a_tile"] = available_tiles

    def setup_listener(self, game_state):
        game_state["listeners"]["on_produce"][self.name] = self.on_produce_effect

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.power_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"Tier {tier_index} at {self.name} is on cooldown")
            return False

        player_power = self.power_per_player[player]
        required_power = self.power_tiers[tier_index]['power_to_reach_tier']

        if player_power < required_power:
            await send_clients_log_message(f"{player} does not have enough power to use tier {tier_index} of {self.name}")
            return False

        if tier_index == 2 and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier 2 of {self.name}")
            return False

        tile_to_receive_shape = game_action_container.required_data_for_action['tile_to_receive_shape']
        shape_to_receive = game_constants.shapes[tier_index]
        
        await game_utilities.player_receives_a_shape_on_tile(
            game_state,
            game_action_container_stack,
            send_clients_log_message,
            send_clients_available_actions,
            send_clients_game_state,
            player,
            game_state["tiles"][tile_to_receive_shape],
            shape_to_receive
        )
        self.power_tiers[tier_index]['is_on_cooldown'] = True    
        return True

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, tier_index):
        producing_tile_name = game_action_container_stack[-1].data_from_event['producing_tile_name']
        reacting_player = game_action_container_stack[-1].whose_action
        await send_clients_log_message(f"{reacting_player} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "tile_to_receive_shape": {},
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": tier_index,
                "producing_tile_index": game_utilities.find_index_of_tile_by_name(game_state, producing_tile_name)
            },
            whose_action=reacting_player,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "red"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="red")
        await send_clients_available_actions(game_utilities.get_available_client_actions(game_state, game_action_container_stack[-1], "blue"), game_action_container_stack[-1].get_next_piece_of_data_to_fill(), player_color_to_send_to="blue")
        await game_action_container_stack[-1].event.wait()

    async def on_produce_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, reactions_by_player, **data):
        producing_tile_name = data.get('producing_tile_name')
        producing_player = data.get('producing_player')
        ruler = self.determine_ruler(game_state)

        for player in ['red', 'blue']:
            tiers_that_can_be_reacted_with = []
            player_power = self.power_per_player[player]

            if not self.power_tiers[0]['is_on_cooldown'] and player_power >= 3:
                tiers_that_can_be_reacted_with.append(0)
            if not self.power_tiers[1]['is_on_cooldown'] and player_power >= 6:
                tiers_that_can_be_reacted_with.append(1)
            if not self.power_tiers[2]['is_on_cooldown'] and player_power >= 9 and player == ruler:
                tiers_that_can_be_reacted_with.append(2)
            
            if tiers_that_can_be_reacted_with:
                reactions_by_player[player].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with