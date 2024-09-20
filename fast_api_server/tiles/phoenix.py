import asyncio
import game_action_container
import game_utilities
import game_constants
from tiles.tile import Tile

class Phoenix(Tile):
    def __init__(self):
        super().__init__(
            name="Phoenix",
            type="Giver",
            minimum_influence_to_rule=5,
            number_of_slots=5,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "**Reaction:** After one of your disciples is ^^burned^^ at a tile, if you are still present there, you may [[receive]] a follower there",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,         
                    "leader_must_be_present": False,             
                    "data_needed_for_use": ['confirm_choice']
                },        
                {
                    "influence_to_reach_tier": 5,
                    "must_be_ruler": False,                    
                    "description": "**Reaction:** Same as above but [[receive]] an acolyte instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": False,                   
                    "data_needed_for_use": ['confirm_choice']
                }, 
                {
                    "influence_to_reach_tier": 7,
                    "must_be_ruler": True,                    
                    "description": "**Reaction:** Same as above but [[receive]] a sage instead",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,            
                    "leader_must_be_present": False,          
                    "data_needed_for_use": ['confirm_choice']
                },     
            ]  
        )

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["do_not_react"] = None
        available_actions["select_a_tier"] = {game_utilities.find_index_of_tile_by_name(game_state, self.name): [tier_index]}

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_burn"][self.name] = self.on_burn_effect

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        player = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)
        
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"Tier {tier_index} at {self.name} is on cooldown")
            return False

        player_influence = self.influence_per_player[player]
        required_influence = self.influence_tiers[tier_index]['influence_to_reach_tier']

        if player_influence < required_influence:
            await send_clients_log_message(f"{player} does not have enough influence to use tier {tier_index} of {self.name}")
            return False

        if tier_index == 2 and player != ruler:
            await send_clients_log_message(f"Only the ruler can use tier 2 of {self.name}")
            return False

        index_of_tile_burned_at = game_action_container.required_data_for_action['index_of_tile_burned_at']    
        if not game_utilities.has_presence(game_state['tiles'][index_of_tile_burned_at], player):
            await send_clients_log_message(f"{player} is not present at the site of burning")  
            return False
        
        disciple_to_receive = game_constants.disciples[tier_index]

        # Receive the disciple
        await game_utilities.player_receives_a_disciple_on_tile(
            game_state, 
            game_action_container_stack, 
            send_clients_log_message, 
            get_and_send_available_actions, 
            send_clients_game_state, 
            player, 
            game_state['tiles'][index_of_tile_burned_at], 
            disciple_to_receive
        )

        await send_clients_log_message(f"{player} used tier {tier_index} of {self.name} to receive a {disciple_to_receive} at {game_state['tiles'][index_of_tile_burned_at].name}")
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True
            
    async def create_append_and_send_available_actions_for_container(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, tier_index):
        color_burned = game_action_container_stack[-1].data_from_event['color']
        index_of_tile_burned_at = game_action_container_stack[-1].data_from_event['index_of_tile_burned_at']
        await send_clients_log_message(f"{color_burned} may react with {self.name}")

        new_container = game_action_container.GameActionContainer(
            event=asyncio.Event(),
            game_action="use_a_tier",
            required_data_for_action={
                "index_of_tile_burned_at": index_of_tile_burned_at,
                "index_of_tile_in_use": game_utilities.find_index_of_tile_by_name(game_state, self.name),
                "index_of_tier_in_use": tier_index,
                "confirm_choice": None,
            },
            whose_action=color_burned,
            is_a_reaction=True,
        )

        game_action_container_stack.append(new_container)
        await get_and_send_available_actions()
        await game_action_container_stack[-1].event.wait()

    #fills in tiers to resolve per player
    async def on_burn_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data): 
        color_burned = data.get('color')
        index_of_tile_burned_at = data.get('index_of_tile_burned_at')

        if not game_utilities.has_presence(game_state['tiles'][index_of_tile_burned_at], color_burned):
            return
        
        tiers_that_can_be_reacted_with = []

        if not self.influence_tiers[0]['is_on_cooldown'] and self.influence_per_player[color_burned] >= self.influence_tiers[0]['influence_to_reach_tier']:
            tiers_that_can_be_reacted_with.append(0)

        if not self.influence_tiers[1]['is_on_cooldown'] and self.influence_per_player[color_burned] >= self.influence_tiers[1]['influence_to_reach_tier']:
            tiers_that_can_be_reacted_with.append(1)

        if not self.influence_tiers[2]['is_on_cooldown'] and self.determine_ruler(game_state) == color_burned and self.influence_per_player[color_burned] >= self.influence_tiers[2]['influence_to_reach_tier']:
            tiers_that_can_be_reacted_with.append(2)
        
        if tiers_that_can_be_reacted_with:
            reactions_by_player[color_burned].tiers_to_resolve[game_utilities.find_index_of_tile_by_name(game_state, self.name)] = tiers_that_can_be_reacted_with