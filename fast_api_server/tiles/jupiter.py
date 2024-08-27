import game_utilities
import game_constants
from tiles.tile import Tile

class Jupiter(Tile):
    def __init__(self):
        super().__init__(
            name="Jupiter",
            type="Producer/Scorer",
            description="**4 power, Action:** Once per round, ^^burn^^ one of your squares here to ++produce++ a triangle\n**Ruler, Most Power, Minimum 6:** +3 points when Jupiter is used",
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        self.determine_power()
        if self.power_per_player["red"] > self.power_per_player["blue"] and self.power_per_player["red"] >= 6:
            self.ruler = 'red'
            return 'red'
        elif self.power_per_player["blue"] > self.power_per_player["red"] and self.power_per_player["blue"] >= 6:
            self.ruler = 'blue'
            return 'blue'
        self.ruler = None
        return None

    def is_useable(self, game_state):
        user = game_state["whose_turn_is_it"]
        return (not self.is_on_cooldown and self.power_per_player[user] >= 4 and any(slot and slot["shape"] == "square" and slot["color"] == user for slot in self.slots_for_shapes))

    async def use_tile(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action

        if self.is_on_cooldown:
            await send_clients_log_message(f"{self.name} is on cooldown")
            return False

        if self.power_per_player[user] < 4:
            await send_clients_log_message(f"Not enough power on {self.name} to use")
            return False

        index_of_jupiter = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        # Find the first square owned by the user
        slot_index_to_burn_shape_from = next((i for i, slot in enumerate(self.slots_for_shapes) 
                                              if slot and slot["shape"] == "square" and slot["color"] == user), None)

        if slot_index_to_burn_shape_from is None:
            await send_clients_log_message(f"No square available to burn on {self.name}")
            return False

        await send_clients_log_message(f"Using {self.name}")

        ruler = self.determine_ruler(game_state)
        if ruler:
            game_state["points"][ruler] += 3
            await send_clients_log_message(f"{ruler} gains 3 points as the ruler of {self.name}")

        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, index_of_jupiter, slot_index_to_burn_shape_from)
        await game_utilities.produce_shape_for_player(game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, user, 1, 'triangle', self.name)

        self.is_on_cooldown = True
        return True