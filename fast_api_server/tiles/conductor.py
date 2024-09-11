import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Conductor(Tile):
    def __init__(self):
        super().__init__(
            name="Conductor",
            type="Mover",
            number_of_slots=5,
            minimum_power_to_rule=3,
            power_tiers=[
                {
                    "power_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "**Reaction:** After you [[receive]] a shape, you may move it to a tile adjacent to Conductor",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": ['tile_to_move_shape_to']
                },
                {
                    "power_to_reach_tier": 6,
                    "must_be_ruler": True,                    
                    "description": "**Reaction:** Same as above but you may move it anywhere",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,                    
                    "data_needed_for_use": ['tile_to_move_shape_to']
                },
            ]            
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        slots_without_a_shape_per_tile = {}

        if tier_index == 0:
            index_of_conductor = game_utilities.find_index_of_tile_by_name(game_state, self.name)            
            for index, tile in enumerate(game_state["tiles"]):
                if game_utilities.determine_if_directly_adjacent(index_of_conductor, index):
                    slots_without_shapes = [slot_index for slot_index, slot in enumerate(tile.slots_for_shapes) if not slot]
                    if slots_without_shapes:
                        slots_without_a_shape_per_tile[index] = slots_without_shapes

        elif tier_index == 1:
            for index, tile in enumerate(game_state["tiles"]):
                slots_without_shapes = [slot_index for slot_index, slot in enumerate(tile.slots_for_shapes) if not slot]
                if slots_without_shapes:
                    slots_without_a_shape_per_tile[index] = slots_without_shapes
        available_actions["select_a_slot_on_a_tile"] = slots_without_a_shape_per_tile        

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]        
        if tier_index == 0:
            if self.power_per_player[game_action_container.whose_action] < 3:
                await send_clients_log_message(f"Cannot react with tier {tier_index} of {self.name}, not enough power")
                return False
            
            if self.power_tiers[tier_index]['is_on_cooldown']:
                await send_clients_log_message(f"Cannot react with tier {tier_index} of {self.name}, it's on cooldown")
                return False                
            
            index_of_conductor = game_utilities.find_index_of_tile_by_name(game_state, self.name)
            slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
            tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
            slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
            tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

            if not game_utilities.determine_if_directly_adjacent(index_of_conductor, tile_index_to):
                await send_clients_log_message(f"Tried to react with {self.name} but destination tile isn't adjacent")
                return False

            if game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] is None:
                await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to move")
                return False

            if game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] is not None:
                await send_clients_log_message(f"Tried to react with {self.name} but chose a non-empty slot to move to")
                return False
            
        elif tier_index == 1:
            if self.power_per_player[game_action_container.whose_action] != self.determine_ruler(game_state):
                await send_clients_log_message(f"Cannot react with tier {tier_index} of {self.name}, not the ruler")
                return False
            
            if self.power_tiers[tier_index]['is_on_cooldown']:
                await send_clients_log_message(f"Cannot react with tier {tier_index} of {self.name}, it's on cooldown")
                return False          

            slot_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['slot_index']
            tile_index_from = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_from']['tile_index']
            slot_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['slot_index']
            tile_index_to = game_action_container.required_data_for_action['slot_and_tile_to_move_shape_to']['tile_index']

            if game_state["tiles"][tile_index_from].slots_for_shapes[slot_index_from] is None:
                await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to move")
                return False

            if game_state["tiles"][tile_index_to].slots_for_shapes[slot_index_to] is not None:
                await send_clients_log_message(f"Tried to react with {self.name} but chose a non-empty slot to move to")
                return False

        await send_clients_log_message(f"Reacting with tier {tier_index} of {self.name}")
        await game_utilities.move_shape_between_tiles(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tile_index_from, slot_index_from, tile_index_to, slot_index_to)
        self.power_tiers[tier_index]['is_on_cooldown'] = True
        return True

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):

        receiver = game_action_container_stack[-1].data_from_event['receiver']
        index_of_slot_received_at = game_action_container_stack[-1].data_from_event['index_of_slot_received_at']
        index_of_tile_received_at = game_action_container_stack[-1].data_from_event['index_of_tile_received_at']
        await send_clients_log_message(f"{receiver} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "slot_and_tile_to_move_shape_from": {"slot_index": index_of_slot_received_at, "tile_index": index_of_tile_received_at},
                "slot_and_tile_to_move_shape_to": {},
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
        
        if not self.power_tiers[0]['is_on_cooldown'] and self.power_per_player[receiver] >= 3:
            tiers_that_can_be_reacted_with.append(0)
        
        if not self.power_tiers[1]['is_on_cooldown'] and self.power_per_player[receiver] >= 6 and self.determine_ruler(game_state) == receiver:
            tiers_that_can_be_reacted_with.append(1)
        
        if tiers_that_can_be_reacted_with:
            reactions_by_player[receiver].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with            

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            game_state["points"][ruler] += 2
            await send_clients_log_message(f"{ruler} gains 2 points at the end of the game from {self.name}")