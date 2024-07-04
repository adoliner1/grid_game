import React from 'react';
import '../stylesheets/tile.css';
import ShapesOnTile from './shapes_on_tile';

const Tile = ({
    name,
    description,
    slots_for_shapes,
    onTileClick,
    shape_to_place,
    onSlotClick,
    selectors,
    clients_color,
    tile_index,
    tile_in_use,
    whose_turn_is_it,
    has_use_action_for_all,
    has_use_action_for_ruler,
    ruler,
}) => {

    const isSelectable = (selectors) => {
        if (whose_turn_is_it !== clients_color) {return false}
        if (!selectors.includes("tile")) {return false}
        if (selectors.includes("usable-by-all") && !has_use_action_for_all && !has_use_action_for_ruler) {return false}
        if (selectors.includes("usable-by-ruler") && (!has_use_action_for_ruler || ruler !== clients_color) && !has_use_action_for_all) {return false}
        return true
    };

    return (
        <div className={isSelectable(selectors) ? 'tile selectable-tile' : 'tile'} onClick={onTileClick}>
            <h3>{name}</h3>
            <p>{description}</p>
            <ShapesOnTile 
                slots_for_shapes={slots_for_shapes} 
                shape_to_place={shape_to_place} 
                onSlotClick={onSlotClick}
                selectors={selectors}
                clients_color={clients_color}
                tile_index= {tile_index}
                tile_in_use = {tile_in_use}
                whose_turn_is_it={whose_turn_is_it}
                ruler = {ruler}
            />
        </div>
    );
};

export default Tile;