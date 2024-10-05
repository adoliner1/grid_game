from .tile import Tile
from .. import game_utilities
from .. import game_constants

class QueensRetinue(Tile):
    def __init__(self):
        super().__init__(
            name="Queen's Retinue",
            type="Scorer",
            minimum_influence_to_rule=3,
            number_of_slots=3,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 3,
                    "must_be_ruler": True,                    
                    "description": "When your opponent ((recruits)) or ++exiles++ a disciple here or on an adjacent tile, +2 point",
                    "is_on_cooldown": False,
                    "leader_must_be_present": False,
                    "has_a_cooldown": False,                    
                },
            ]            
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    def setup_listener(self, game_state):
        game_state["listeners"]["on_recruit"][self.name] = self.on_recruit_effect
        game_state["listeners"]["on_exile"][self.name] = self.on_exile_effect

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, send_clients_log_message, data, "recruited")

    async def on_exile_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        await self.handle_effect(game_state, send_clients_log_message, data, "exiled")

    async def handle_effect(self, game_state, send_clients_log_message, data, action_type):
        actor = data.get('recruiter') if action_type == "recruited" else data.get('exiler')
        tile_index = data.get('index_of_tile_recruited_at') if action_type == "recruited" else data.get('index_of_tile_exiled_from')
        queen_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
       
        if not (tile_index == queen_index or game_utilities.determine_if_directly_adjacent(tile_index, queen_index)):
            return

        other_player = game_utilities.get_other_player_color(actor)
        ruler = self.determine_ruler(game_state)
        other_player_influence = self.influence_per_player[other_player]
        points_earned = 0

        if other_player_influence >= self.influence_tiers[0]['influence_to_reach_tier'] and ruler == other_player:
            points_earned = 2

        if points_earned > 0:
            game_state["points"][other_player] += points_earned
            await send_clients_log_message(f"{other_player} earned {points_earned} points from **{self.name}** because {actor} {action_type} a disciple {'here' if tile_index == queen_index else 'on an adjacent tile'}")