from collections import OrderedDict

class GameActionContainer:
    def __init__(self, event, game_action, required_data_for_action, whose_action, is_a_reaction=False):
        self.event = event
        self.game_action = game_action
        self.required_data_for_action = required_data_for_action
        self.whose_action = whose_action
        self.is_a_reaction = is_a_reaction
        self.current_piece_of_data_to_fill = None

    def get_next_piece_of_data_to_fill(self):
        for piece_of_data_to_fill, value in self.required_data_for_action.items():
            if value is None or value == {}:
                self.current_piece_of_data_to_fill = piece_of_data_to_fill
                return piece_of_data_to_fill
        return None
    
    def update_with_data_from_client(self, data):
        #the client is starting or making an initial action    
        if self.game_action == None:
            match data.client_action:
                case 'pass':
                    self.game_action = 'pass'
                case 'select_a_shape_in_storage':
                    self.game_action = 'place_shape_on_slot'
                    self.required_data_for_action["shape_type_to_place"] = data.selected_shape_type_in_storage
                case 'select_a_tile':
                    self.game_action = 'use_tile'
                    self.required_data_for_action["index_of_tile_in_use"] = data.selected_tile_index
                case 'select_a_powerup':
                    self.game_action = 'use_powerup'
                    self.required_data_for_action["index_of_powerup_in_use"] = data.selected_powerup_index
                case _:
                    #invalid client action given
                    pass

        #this data from client is to update required_data_for_action
        else:
            match data.client_action:
                case 'select_a_shape_in_storage':
                    self.required_data_for_action[self.current_piece_of_data_to_fill] = data.selected_shape_type_in_storage
                case 'select_a_tile':
                    self.required_data_for_action[self.current_piece_of_data_to_fill] = data.selected_tile_index
                case 'select_a_powerup':
                    self.required_data_for_action[self.current_piece_of_data_to_fill] = data.selected_powerup_index
                case 'select_a_slot_on_a_powerup':
                    self.required_data_for_action[self.current_piece_of_data_to_fill]["powerup_index"] = data.powerup_index_of_selected_slot
                    self.required_data_for_action[self.current_piece_of_data_to_fill]["slot_index"] = data.index_of_selected_slot
                case 'select_a_slot_on_a_tile':
                    self.required_data_for_action[self.current_piece_of_data_to_fill]["tile_index"] = data.tile_index_of_selected_slot
                    self.required_data_for_action[self.current_piece_of_data_to_fill]["slot_index"] = data.index_of_selected_slot                  
                case _:
                    #invalid client action given
                    pass
