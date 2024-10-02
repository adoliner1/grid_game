import game_utilities
import game_constants
from tiles.tile import Tile

class RealmOfTheJester(Tile):
    def __init__(self):
        super().__init__(
            name="Realm of the Jester",
            type="Generator/Scorer",
            minimum_influence_to_rule=1,
            description = f"When you ((recruit)) here, +4 power",
            number_of_slots=2,
            influence_tiers=[
                {
                    "influence_to_reach_tier": 1,
                    "must_be_ruler": True,                    
                    "description": "At the __end of each round__, -3 points",
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

    def modify_expected_incomes(self, game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            points_to_lose = 3
            game_state['expected_points_incomes'][ruler] -= points_to_lose            

    async def on_recruit_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state, reactions_by_player, **data):
        recruiter = data.get('recruiter')
        tile_index = data.get('index_of_tile_recruited_at')
        realm_of_the_jester_index = game_utilities.find_index_of_tile_by_name(game_state, self.name)
        
        if tile_index == realm_of_the_jester_index:
            power_gained = 4
            game_state['power'][recruiter] += power_gained
            await send_clients_log_message(f"{recruiter} gets {power_gained} from recruiting at **{self.name}**")

    async def end_of_round_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        ruler = self.determine_ruler(game_state)
        if ruler:
            points_to_lose = 3
            game_state['points'][ruler] -= points_to_lose
            await send_clients_log_message(f"{ruler} loses {points_to_lose} points from **{self.name}**")