import game_utilities
import game_constants
from tiles.tile import Tile

class Lion(Tile):
    def __init__(self):
        super().__init__(
            name="Lion",
            type="Producer/Giver",
            number_of_slots=3,
            minimum_power_to_rule=2,
            description="The player with less power here ++produces++ 1 square at the __start of a round__",
            power_tiers=[
                {
                    "power_to_reach_tier": 2,
                    "must_be_ruler": True,                    
                    "description": "**Action:** [[Receive]] 2 circles at an adjacent tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                     
                    "data_needed_for_use": ["tile_to_receive_shapes_at"],
                },
            ],      
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []

        if not self.power_tiers[0]["is_on_cooldown"] and self.determine_ruler(game_state) == game_state["whose_turn_is_it"]:
            useable_tiers.append(0)

        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_utilities.find_index_of_tile_by_name(game_state, self.name))
        available_actions["select_a_tile"] = indices_of_adjacent_tiles

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
       
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Only the ruler can use {self.name}")
            return False

        if self.power_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"{self.name} is on cooldown and cannot be used this round")
            return False

        index_of_tile_to_receive_shapes_on = game_action_container.required_data_for_action['tile_to_receive_shapes_at']
        tile_to_receive_shapes_on = game_state['tiles'][index_of_tile_to_receive_shapes_on]
        
        if not game_utilities.determine_if_directly_adjacent(index_of_tile_to_receive_shapes_on, game_utilities.find_index_of_tile_by_name(game_state, self.name)):
            await send_clients_log_message(f"Chose non-adjacent tile while using {self.name}")
            return False

        await send_clients_log_message(f"{self.name} is used")
        self.power_tiers[0]['is_on_cooldown'] = True
        
        for _ in range(2):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, ruler, tile_to_receive_shapes_on, 'circle')
        
        return True

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        if self.power_per_player['red'] < self.power_per_player['blue']:
            player_with_less_power = 'red'
        elif self.power_per_player['blue'] < self.power_per_player['red']:
            player_with_less_power = 'blue'
        else:
            player_with_less_power = None
        
        if player_with_less_power:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, player_with_less_power, 1, 'square', self.name, True)
            await send_clients_log_message(f"{player_with_less_power} produces 1 square from {self.name} at the start of the round")