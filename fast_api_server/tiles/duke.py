import game_utilities
import game_constants
from tiles.tile import Tile

class Duke(Tile):
    def __init__(self):
        super().__init__(
            name="Duke",
            type="Scorer",
            minimum_influence_to_rule=3,
            influence_tiers=[],
            description="For each disciple type you have more of here at the end of the game, +3 points\nIf you have more of every kind of disciple here at the end of the game, +5 points",
            number_of_slots=7,
        )

    def determine_ruler(self, game_state):
        return super().determine_ruler(game_state, self.minimum_influence_to_rule)

    async def end_of_game_effect(self, game_state, game_action_container_stack, send_clients_log_message, get_and_send_available_actions, send_clients_game_state):
        disciple_counts = {
            'red': {'follower': 0, 'acolyte': 0, 'sage': 0},
            'blue': {'follower': 0, 'acolyte': 0, 'sage': 0}
        }
        for slot in self.slots_for_disciples:
            if slot:
                color = slot["color"]
                disciple = slot["disciple"]
                disciple_counts[color][disciple] += 1

        disciples_dominated = {'red': 0, 'blue': 0}

        for disciple in game_constants.disciples:
            if disciple_counts['red'][disciple] > disciple_counts['blue'][disciple]:
                game_state['points']['red'] += 3
                disciples_dominated['red'] += 1
                await send_clients_log_message(f"Red has more {disciple}s on **{self.name}**, +3 points")
            elif disciple_counts['blue'][disciple] > disciple_counts['red'][disciple]:
                game_state['points']['blue'] += 3
                disciples_dominated['blue'] += 1
                await send_clients_log_message(f"Blue has more {disciple}s on **{self.name}**, +3 points")

        for color in ['red', 'blue']:
            if disciples_dominated[color] == len(game_constants.disciples):
                game_state['points'][color] += 5
                await send_clients_log_message(f"{color} has more of all disciple types on **{self.name}**, +5 points")