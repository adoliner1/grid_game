from .tile import Tile
from .. import game_utilities
from .. import game_constants

class RiftOfLight(Tile):
    def __init__(self):
        super().__init__(
            name="Rift of Light",
            type="Leader-Mover",
            minimum_influence_to_rule=4,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 4,
                    "must_be_ruler": True,
                    "description": "**Action:** Teleport to any tile",
                    "is_on_cooldown": False,
                    "has_a_cooldown": True,
                    "leader_must_be_present": False,
                    "data_needed_for_use": ["tile_to_move_leader_to"]
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def get_useable_tiers(self, game_state):
        useable_tiers = []
        whose_turn_is_it = game_state["whose_turn_is_it"]
        ruler = self.determine_ruler(game_state)
       
        if (self.influence_per_player[whose_turn_is_it] >= self.influence_tiers[0]['influence_to_reach_tier'] and
            not self.influence_tiers[0]["is_on_cooldown"] and
            whose_turn_is_it == ruler):
                useable_tiers.append(0)
       
        return useable_tiers

    def set_available_actions_for_use(self, game_state, tier_index, game_action_container, available_actions):
        available_actions["select_a_tile"] = game_constants.all_tile_indices

    async def use_a_tier(self, game_state, tier_index, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        game_action_container = game_action_container_stack[-1]
        user = game_action_container.whose_action
        ruler = self.determine_ruler(game_state)

        if self.influence_per_player[user] < self.influence_tiers[0]['influence_to_reach_tier']:
            await send_clients_log_message(f"Not enough influence to use **{self.name}**")
            return False

        if self.influence_tiers[tier_index]["is_on_cooldown"]:
            await send_clients_log_message(f"**{self.name}** is on cooldown")
            return False

        if user != ruler:
            await send_clients_log_message(f"Only the ruler can use **{self.name}**")
            return False      

        index_of_tile_to_move_leader_to = game_action_container.required_data_for_action['tile_to_move_leader_to']
        tile_to_move_leader_to = game_state['tiles'][index_of_tile_to_move_leader_to]
        if index_of_tile_to_move_leader_to is None or index_of_tile_to_move_leader_to > 8:
            await send_clients_log_message(f"Invalid tile selected for using **{self.name}**")
            return False    

        await send_clients_log_message(f"{user}_leader took **{self.name}** to **{tile_to_move_leader_to.name}**.")

        location_of_leader = game_utilities.get_tile_index_of_leader(game_state, user)

        await send_clients_log_message(f"{user} sent {user}_leader to to **{tile_to_move_leader_to.name}** with **{self.name}**")
        game_state['tiles'][location_of_leader].leaders_here[user] = False
        tile_to_move_leader_to.leaders_here[user] = True
        self.influence_tiers[tier_index]["is_on_cooldown"] = True
        return True