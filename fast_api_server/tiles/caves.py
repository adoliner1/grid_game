import game_utilities
import game_constants
from tiles.tile import Tile

class Caves(Tile):
    def __init__(self):
        super().__init__(
            name="Caves",
            type="Giver",
            number_of_slots=5,
            minimum_power_to_rule=2,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "When you ((place)) a triangle at an adjacent tile, [[receive]] a circle at that tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": False,                    
                    "description": "[[Receive]] a square instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },
                {
                    "power_to_reach_tier": 7,
                    "must_be_ruler": False,                    
                    "description": "[[Receive]] a triangle instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": False,                    
                },                               
            ]              
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_place"][self.name] = self.on_place_effect

    async def on_place_effect(self, game_state, game_action_container_stack, send_clients_log_message, send_clients_available_actions, send_clients_game_state, reactions_by_player, **data):
        placer = data.get('placer')
        shape = data.get('shape')
        index_of_tile_placed_at = data.get('index_of_tile_placed_at')
       
        if shape != "triangle":
            return
       
        self.determine_power()
        placer_power = self.power_per_player[placer]
        if placer_power < 3:
            return

        index_of_caves = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        is_adjacent = game_utilities.determine_if_directly_adjacent(index_of_caves, index_of_tile_placed_at)
        tile_placed_at = game_state["tiles"][index_of_tile_placed_at]

        if not is_adjacent:
            return

        if placer_power >= 7:
            shape_to_receive = "triangle"
        elif placer_power >= 5:
            shape_to_receive = "square"
        else:
            shape_to_receive = "circle"
       
        await game_utilities.player_receives_a_shape_on_tile(
            game_state, game_action_container_stack, send_clients_log_message,
            send_clients_available_actions, send_clients_game_state,
            placer, tile_placed_at, shape_to_receive
        )
        
        await send_clients_log_message(f"{placer} receives a {shape_to_receive} at {tile_placed_at.name} from {self.name} because hey have {placer_power} power at caves")