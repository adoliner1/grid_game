import game_utilities
import game_constants
from tiles.tile import Tile

class LilyPad(Tile):
    def __init__(self):
        super().__init__(
            name="Lily Pad",
            type="Generator",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "**Action:** Pay 1 power to get 2 power",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,   
                    "leader_must_be_present": True,                  
                    "data_needed_for_use": [],
                },
            ]
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        user = game_state["whose_turn_is_it"]
        if (not self.influence_tiers[0]['is_on_cooldown'] and 
            self.influence_per_player[user] >= self.influence_tiers[0]['influence_to_reach_tier'] and user == self.determine_ruler(game_state) and game_state['power'][user] > 0):
            useable_tiers.append(0)
        return useable_tiers

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
       
        if self.influence_tiers[tier_index]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** tier {tier_index} is on cooldown")
            return False
       
        if self.influence_per_player[user] < self.influence_tiers[tier_index]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence on **{self.name}** to use tier {tier_index}")
            return False
       
        if self.determine_ruler(game_state) != user:
            await send_clients_log_message(f"You must be the ruler to use **{self.name}**")
            return False
        
        if game_state['power'][user] < 1:
            await send_clients_log_message(f"Not enough power to use **{self.name}**")
            return False

        game_state['power'][user] += 1
        await send_clients_log_message(f"{user} loses 1 power and then gains 2 from **{self.name}**") 
       
        self.influence_tiers[tier_index]['is_on_cooldown'] = True
        return True