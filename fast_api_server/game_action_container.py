class GameActionContainer:
    def __init__(self, event, game_action, required_data_for_action, whose_action):
        self.event = event
        self.game_action = game_action
        self.required_data_for_action = required_data_for_action
        self.whose_action = whose_action

    def get_next_piece_of_data_to_fill(self):
        for piece_of_data_to_fill, value in self.required_data_for_action.items():
            if value is None or value == {}:
                return piece_of_data_to_fill
        return None