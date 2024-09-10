from collections import OrderedDict

class GameActionContainer:
    def __init__(self, event, game_action, required_data_for_action, whose_action, data_from_event=None, tiers_to_resolve=None, is_a_reaction=False):
        self.event = event
        self.game_action = game_action
        self.required_data_for_action = required_data_for_action
        self.whose_action = whose_action
        self.is_a_reaction = is_a_reaction
        self.tiers_to_resolve=tiers_to_resolve
        self.data_from_event=data_from_event

    def get_next_piece_of_data_to_fill(self):
        for piece_of_data_to_fill, value in self.required_data_for_action.items():
            if value is None or value == {}:
                return piece_of_data_to_fill
        return None

    def __str__(self):
        return (f"GameActionContainer(\n"
                f"  event: {self.event},\n"
                f"  game_action: {self.game_action},\n"
                f"  required_data_for_action: {self.required_data_for_action},\n"
                f"  whose_action: {self.whose_action},\n"
                f"  is_a_reaction: {self.is_a_reaction}\n"
                f"  tiers_to_resolve: {self.tiers_to_resolve}\n"
                f"  data_from_event: {self.data_from_event}\n"
                f")")