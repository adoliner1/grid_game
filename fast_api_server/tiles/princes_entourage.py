import asyncio
import game_action_container
from .tile import Tile
import game_utilities
import game_constants

class PrincesEntourage(Tile):
    def __init__(self):
        super().__init__(
            name="Prince's Entourage",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=4,
            description="",
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,
                    "description": "When you [[receive]] or ((recruit)) adjacent to Prince's Entourage, +1 points",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_a_cooldown": False,
                },
            ],
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_receive"][self.name] = self.on_receive_effect
        game_state["listeners"]["on_recruit"][self.name] = self.on_recruit_effect

    async def on_receive_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, send_clients_log_message, data, "received")

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, send_clients_log_message, data, "recruited")

    async def handle_effect(self, game_state, send_clients_log_message, data, action_type):
        actor = data.get('receiver') if action_type == "received" else data.get('recruiter')
        tile_index = data.get('index_of_tile_received_at') if action_type == "received" else data.get('index_of_tile_recruited_at')
        prince_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)

        if not game_utilities.determine_if_directly_adjacent(tile_index, prince_index):
            return

        ruler = self.determine_ruler(game_state)
        actor_influence = self.influence_per_player[actor]
        points_earned = 0

        if actor == ruler and actor_influence >= self.influence_tiers[0]['influence_to_reach_tier']:
            points_earned = 1

        if points_earned > 0:
            game_state["points"][actor] += points_earned
            await send_clients_log_message(f"{actor} earned {points_earned} point from **{self.name}** for {action_type} a disciple on an adjacent tile")
