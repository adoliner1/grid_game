import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class SummoningTower(Tile):
    def __init__(self):
        super().__init__(
            name="Summoning Tower",
            type="Giver",
            number_of_slots=4,
            minimum_influence_to_rule=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": False,                    
                    "description": "**Action:** [[Receive]] a follower at a tile you rule",
                    "is_on_cooldown": False,
                    "leader_must_be_present": True,
                    "data_needed_for_use": ["tile_to_receive_follower"],
                    "has_a_cooldown": True,
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        current_player = game_state["whose_turn_is_it"]
        if (not self.influence_tiers[0]["is_on_cooldown"] and 
            self.influence_per_player[current_player] >= self.influence_tiers[0]["influence_to_reach_tier"] and 
            self.leaders_here[current_player]):
            useable_tiers.append(0)
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        tiles_ruled_by_player = []
        for index, tile in enumerate(game_state["tiles"]):
            if tile.determine_ruler(game_state) == game_action_container.whose_action:
                tiles_ruled_by_player.append(index)
        available_actions["select_a_tile"] = tiles_ruled_by_player

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action                                              

        if self.influence_tiers[0]['is_on_cooldown']:
            await send_clients_log_message(f"**{self.name}** is on cooldown and cannot be used this round")
            return False
       
        if not self.leaders_here[user]:
            await send_clients_log_message(f"Leader must be on **{self.name}** to use it")
            return False

        tile_to_receive_follower = game_action_container.required_data_for_action['tile_to_receive_follower']

        if game_state["tiles"][tile_to_receive_follower].determine_ruler(game_state) != user:
            await send_clients_log_message(f"You can only receive a follower at a tile you rule")
            return False

        await send_clients_log_message(f"**{self.name}** is used")
        await game_utilities.player_receives_a_disciple_on_tile(game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, user, game_state["tiles"][tile_to_receive_follower], 'follower')
        
        self.influence_tiers[0]['is_on_cooldown'] = True
        return True