import game_utilities
import game_constants
from tiles.tile import Tile

class Wolf(Tile):
    def __init__(self):
        super().__init__(
            name="Wolf",
            type="Producer/Giver",
            description="The player with fewer shapes here ++produces++ 1 triangle at the __start of a round__\n**Ruler, Most Shapes, Action:** Once per round, [[receive]] 2 squares at an adjacent tile",
            number_of_slots=3,
            data_needed_for_use=["tile_to_receive_shapes_at"]
        )

    def determine_ruler(self, game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        
        if red_count > blue_count:
            self.ruler = 'red'
            return 'red'
        elif blue_count > red_count:
            self.ruler = 'blue'
            return 'blue'
       
        self.ruler = None
        return None

    def is_useable(self, game_state):
        return self.determine_ruler(game_state) == game_state["whose_turn_is_it"] and not self.is_on_cooldown

    def set_available_actions_for_use(self, game_state, game_action_container, available_actions):
        indices_of_adjacent_tiles = game_utilities.get_adjacent_tile_indices(game_utilities.find_index_of_tile_by_name(game_state, self.name))
        available_actions["select_a_tile"] = indices_of_adjacent_tiles

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        ruler = self.determine_ruler(game_state)
        
        if not ruler:
            await send_clients_log_message(f"No ruler determined for {self.name}, cannot use")
            return False
       
        if ruler != game_action_container.whose_action:
            await send_clients_log_message(f"Only the ruler can use {self.name}")
            return False

        if self.is_on_cooldown:
            await send_clients_log_message(f"{self.name} is on cooldown and cannot be used this round")
            return False

        index_of_tile_to_receive_shapes_on = game_action_container.required_data_for_action['tile_to_receive_shapes_at']
        tile_to_receive_shapes_on = game_state['tiles'][index_of_tile_to_receive_shapes_on]
        
        if not game_utilities.determine_if_directly_adjacent(index_of_tile_to_receive_shapes_on, game_utilities.find_index_of_tile_by_name(game_state, self.name)):
            await send_clients_log_message(f"Chose non-adjacent tile while using {self.name}")
            return False

        await send_clients_log_message(f"{self.name} is used")
        self.is_on_cooldown = True
        for _ in range(2):
            await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, ruler, tile_to_receive_shapes_on, 'square')
        
        return True

    async def start_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        red_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "red")
        blue_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == "blue")
        
        if red_count < blue_count:
            player_with_fewest_shapes = 'red'
        elif blue_count < red_count:
            player_with_fewest_shapes = 'blue'
        else:
            player_with_fewest_shapes = None
        
        if player_with_fewest_shapes:
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player_with_fewest_shapes, 1, 'triangle', self.name, True)
            await send_clients_log_message(f"{player_with_fewest_shapes} produces 1 triangle from {self.name} at the start of the round")

        self.is_on_cooldown = False