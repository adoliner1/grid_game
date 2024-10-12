import asyncio
import game_action_container
import game_utilities
import game_constants

class Status:

    def __init__(self, name, duration, description, player_with_status):
        self.name = name
        self.duration = duration
        self.description = description
        self.player_with_status = player_with_status

    def setup_listener(self, game_state):
        pass

    def cleanup_listener(self, game_state):
        pass

    def modify_recruiting_ranges(self, game_state):
        pass

    def modify_expected_incomes(self, game_state):
        pass

    def modify_recruiting_costs(self, game_state):
        pass

    def modify_leader_movements(self, game_state):
        pass

    def modify_exiling_ranges(self, game_state):
        pass

    def modify_exiling_costs(self, game_state):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "player_with_status": self.player_with_status
        }
    