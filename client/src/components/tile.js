import React from 'react'
import '../stylesheets/tile.css'
import ShapesOnTile from './shapes_on_tile'

const Tile = ({
    name,
    type,
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
            return available_actions.hasOwnProperty('select_a_tile') && available_actions['select_a_tile'].includes(tile_index)
    }

    const tileClickHandler = isSelectable() ? onTileClick : undefined

    function parseCustomMarkup(text) {
        return text
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
          .replace(/__(.*?)__/g, '<i>$1</i>')  // Italic
          .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700;">$1</span>')  // Burn (orange)
          .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff;">$1</span>')  // Receive (purple)
          .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a;">$1</span>')  // Place (blue)
          .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000;">$1</span>')  // Produce (green)
          .replace(/\b(action|reaction)\b/gi, '<u>$1</u>')  // Underline action and reaction
          .replace(/\n/g, '<br><br>');  // Double line breaks
      }
      

    description = parseCustomMarkup(description)

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${ruler ? `tile-${ruler}` : ''} ${is_on_cooldown ? 'tile-on-cooldown' : ''}`} onClick={tileClickHandler}>
            <div className="tile-header">
                <h3 className={`tile-name ${ruler ? `tile-name-${ruler}` : ''}`}>{name}</h3>
                <span className="tile-type">{type}</span>
            </div>
            <p className="tile-description" dangerouslySetInnerHTML={{ __html: description }}></p>
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
