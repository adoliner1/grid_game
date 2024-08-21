import game_utilities
import game_constants
from tiles.tile import Tile

class Evolution(Tile):
    def __init__(self):
        super().__init__(
            name="Evolution",
            type="Producer/Giver/Scorer",
            description=f"Action: Burn 3 of your triangles here to produce 4 circles and 8 points. At the end of a round, burn each shape here and receive the next most powerful shape. Triangles become circles\nRuler: Most Shapes. At the end of the game, -6 points",
            number_of_slots=7,
        )

    def is_useable(self, game_state):
        player_color = game_state["whose_turn_is_it"]
        triangle_count = sum(1 for slot in self.slots_for_shapes if slot and slot["color"] == player_color and slot["shape"] == "triangle")
        return triangle_count >= 3

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

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player_color = game_action_container.whose_action
                
        if not self.is_useable(game_state):
            await send_clients_log_message(f"Don't have enough triangles on {self.name}")
            return False

        await send_clients_log_message(f"Using {self.name}")

        for slot_index, slot in enumerate(self.slots_for_shapes):
            if slot and slot["color"] == player_color and slot["shape"] == "triangle":
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), slot_index)

        for _ in range(4):
            await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player_color, 1, 'circle', self.name)

        game_state["points"][player_color] += 8
        await send_clients_log_message(f"{player_color} gains 8 points from using {self.name}")

        return True

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        await send_clients_log_message(f"Applying end of round effect for {self.name}")
        
        for i in range(len(self.slots_for_shapes)):
            if self.slots_for_shapes[i]:
                current_shape = self.slots_for_shapes[i]["shape"]
                player_color = self.slots_for_shapes[i]["color"]
                
                # Burn the current shape
                await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, game_utilities.find_index_of_tile_by_name(game_state, self.name), i)
                
                # Produce the next most powerful shape
                if current_shape == "circle":
                    new_shape = "square"
                elif current_shape == "square":
                    new_shape = "triangle"
                else:  # triangle
                    new_shape = "circle"
                
                await game_utilities.player_receives_a_shape_on_tile(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, player_color, self, new_shape)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            await send_clients_log_message(f"{self.name} deducts 4 points from {ruler}")
            game_state["points"][ruler] -= 6