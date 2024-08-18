import React from 'react'
import '../stylesheets/tile.css'
import ShapesOnTile from './shapes_on_tile'

const Tile = ({
    name,
    description,
    red_power,
    blue_power,
    is_on_cooldown,
    slots_for_shapes,
    tile_index,
    ruler,
    available_actions,
    onTileClick,
    onSlotClick,
}) => {

    const isSelectable = () => {
            return available_actions.hasOwnProperty('select_a_tile') && available_actions['select_a_tile'].includes(tile_index) && !is_on_cooldown
    }

    const tileClickHandler = isSelectable() ? onTileClick : undefined

    // Replace \n with <br> tags and add HTML tags for bold text
    const formattedDescription = description.replace(/\n/g, '<br><br>').replace(/Ruling Criteria:/g, '<strong>Ruling Criteria:</strong>').replace(/Ruling Benefits:/g, '<strong>Ruling Benefits:</strong>')

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${ruler ? `tile-${ruler}` : ''} ${is_on_cooldown ? 'tile-on-cooldown' : ''}`} onClick={tileClickHandler}>
            <h3 className={ruler ? `tile-name-${ruler}` : ''}>{name}</h3>
            <p className="tile-description" dangerouslySetInnerHTML={{ __html: formattedDescription }}></p>
            <p className='red-power'> Red Power: {red_power} </p>
            <p className='blue-power'> Blue Power: {blue_power} </p>
            <ShapesOnTile 
                slots_for_shapes={slots_for_shapes} 
                tile_index={tile_index}
                ruler={ruler}
                available_actions={available_actions}
                onSlotClick={onSlotClick}
            />
        </div>
    )
}

export default Tile
