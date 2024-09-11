import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Captain(Tile):
    def __init__(self):
        super().__init__(
            name="Captain",
            type="Attacker/Scorer",
            minimum_power_to_rule=2,
            power_tiers=[
                {
                    "power_to_reach_tier": 2,
                    "must_be_ruler": False,                    
                    "description": "**Reaction:** After you [[receive]] a shape at a tile, you may ^^burn^^ a shape at a tile adjacent to that tile, +1 point",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "data_needed_for_use": ['slot_and_tile_to_burn_shape'],
                },
                {
                    "power_to_reach_tier": 5,
                    "must_be_ruler": True,                    
                    "description": "**Reaction:** Same as above but +3 points",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "data_needed_for_use": ['slot_and_tile_to_burn_shape'],
                },                       
            ],            
            number_of_slots=5,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_power_to_rule)

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        slots_with_a_burnable_shape = {}
        index_of_tile_received_at = game_action_container.required_data_for_action.get('index_of_tile_received_at')
        if index_of_tile_received_at is not None:
            for tile_index in game_utilities.get_adjacent_tile_indices(index_of_tile_received_at):
                slots_with_shapes = [i for i, slot in enumerate(game_state["tiles"][tile_index].slots_for_shapes) if slot]
                if slots_with_shapes:
                    slots_with_a_burnable_shape[tile_index] = slots_with_shapes
        available_actions["select_a_slot_on_a_tile"] = slots_with_a_burnable_shape

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if self.power_tiers[tier_index]["must_be_ruler"] and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier {tier_index} of {self.name}")
            return False

        if self.power_per_player[player] < self.power_tiers[tier_index]["power_to_reach_tier"]:
            await send_clients_log_message(f"Not enough power to use tier {tier_index} of {self.name}")
            return False

        if self.power_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"Tier {tier_index} of {self.name} is on cooldown")
            return False

        slot_index_to_burn_shape = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape']['slot_index']
        index_of_tile_to_burn_shape = game_action_container.required_data_for_action['slot_and_tile_to_burn_shape']['tile_index']
        index_of_tile_received_at = game_action_container.required_data_for_action['index_of_tile_received_at']

        if not game_utilities.determine_if_directly_adjacent(index_of_tile_to_burn_shape, index_of_tile_received_at):
            await send_clients_log_message(f"Tried to react with {self.name} but chose a non-adjacent tile to burn at")
            return False            

        if game_state["tiles"][index_of_tile_to_burn_shape].slots_for_shapes[slot_index_to_burn_shape] is None:
            await send_clients_log_message(f"Tried to react with {self.name} but there is no shape to burn at {game_state['tiles'][index_of_tile_to_burn_shape].name} at slot {slot_index_to_burn_shape}")
            return False

        await send_clients_log_message(f"Reacting with tier {tier_index} of {self.name}")
        await game_utilities.burn_shape_at_tile_at_index(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, index_of_tile_to_burn_shape, slot_index_to_burn_shape)
        
        points_gained = 3 if tier_index == 1 else 1
        game_state["points"][player] += points_gained
        await send_clients_log_message(f"{player} gains {points_gained} points from using {self.name}")

        self.power_tiers[tier_index]["is_on_cooldown"] = True
        return True
    
    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect

    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        receiver = game_action_container_stack[-1].data_from_event['receiver']
        index_of_tile_received_at = game_action_container_stack[-1].data_from_event['index_of_tile_received_at']
        await send_clients_log_message(f"{receiver} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "slot_and_tile_to_burn_shape": {},
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
        player_power = self.power_per_player[receiver]

        if not self.power_tiers[0]["is_on_cooldown"] and player_power >= 2:
            tiers_that_can_be_reacted_with.append(0)
        if not self.power_tiers[1]["is_on_cooldown"] and player_power >= 5 and receiver == ruler:
            tiers_that_can_be_reacted_with.append(1)

        if tiers_that_can_be_reacted_with:
            reactions_by_player[receiver].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with