import React from 'react'
import Follower from './disciples/follower'
import Acolyte from './disciples/acolyte'
import Sage from './disciples/sage'
import '../stylesheets/disciples_on_tile.css'

const DisciplesOnTile = ({ slots_for_disciples, tile_index, available_actions, onSlotClick}) => {
    const renderDisciple = (disciple, color) => {
        switch (disciple) {
            case 'follower':
                return <Follower playerColor={color} />
            case 'acolyte':
                return <Acolyte playerColor={color} />
            case 'sage':
                return <Sage playerColor={color} />
            default:
                return null
        }
    }

    const isSelectable = (index) => {
        return available_actions.hasOwnProperty('select_a_slot_on_a_tile') &&
        available_actions['select_a_slot_on_a_tile'].hasOwnProperty(tile_index) &&
        available_actions['select_a_slot_on_a_tile'][tile_index].includes(index)
    }

    return (
        <div className="disciples-on-tile">
            {slots_for_disciples.map((slot, index) => (
                <div
                    key={index}
                    className={`slot ${isSelectable(index) ? 'selectable-slot' : ''}`}
                    onClick={() => isSelectable(index) && onSlotClick(index)}
                >
                    {slot ? renderDisciple(slot.disciple, slot.color) : null}
                </div>
            ))}
        </div>
    )
}

export default DisciplesOnTile