import React from 'react'
import '../stylesheets/tile.css'
import ShapesOnTile from './shapes_on_tile'

const Tile = ({
    name,
    description,
    slots_for_shapes,
    tile_index,
    ruler,
    available_actions,
    onTileClick,
    onSlotClick,
}) => {

    const isSelectable = () => {
            return available_actions.hasOwnProperty('select_a_tile') && available_actions['select_a_tile'].includes(tile_index)
    }

    const tileClickHandler = isSelectable() ? onTileClick : undefined

    // Replace \n with <br> tags and add HTML tags for bold text
    const formattedDescription = description.replace(/\n/g, '<br><br>').replace(/Ruling Criteria:/g, '<strong>Ruling Criteria:</strong>').replace(/Ruling Benefits:/g, '<strong>Ruling Benefits:</strong>')

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${ruler ? `tile-${ruler}` : ''}`} onClick={tileClickHandler}>
            <h3 className={ruler ? `tile-name-${ruler}` : ''}>{name}</h3>
            <p className="tile-description" dangerouslySetInnerHTML={{ __html: formattedDescription }}></p>
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
