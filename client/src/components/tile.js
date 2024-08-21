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

    const formattedDescription = description
    .replace(/\n/g, '<br><br>')
    .replace(/Ruler:/g, '<strong>Ruler:</strong>')
    .replace(/Action:/g, '<strong>Action:</strong>')
    .replace(/Reaction:/g, '<strong>Reaction:</strong>')
    .replace(/Most Shapes:/g, '<strong>Most Shapes:</strong>')
    .replace(/Fewest Shapes:/g, '<strong>Fewest Shapes:</strong>')
    .replace(/Most Power:/g, '<strong>Most Power:</strong>')
    .replace(/(\d+)\s+Power/g, '<strong>$1 Power</strong>')
    .replace(/start of a round/gi, '<i>start of a round</i>')
    .replace(/end of a round/gi, '<i>end of a round</i>')
    .replace(/end of the game/gi, '<i>end of the game</i>')
    .replace(/\b(burn|burns|burned)\b/gi, '<span style="color: #ff8700;">$1</span>')
    .replace(/\b(receive|receives|received)\b/gi, '<span style="color: #9f00ff;">$1</span>')
    .replace(/\b(place|places|placed|placing)\b/gi, '<span style="color: #007a9a;">$1</span>')
    .replace(/\b(produce|produces|produced|producing)\b/gi, '<span style="color: #019000;">$1</span>');

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${ruler ? `tile-${ruler}` : ''} ${is_on_cooldown ? 'tile-on-cooldown' : ''}`} onClick={tileClickHandler}>
            <div className="tile-header">
                <h3 className={`tile-name ${ruler ? `tile-name-${ruler}` : ''}`}>{name}</h3>
                <span className="tile-type">{type}</span>
            </div>
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
