import React from 'react'
import Circle from './shapes/circle'
import Square from './shapes/square'
import Triangle from './shapes/triangle'
import '../stylesheets/shapes_on_tile.css'

const ShapesOnTile = ({ slots_for_shapes, tile_index, available_actions, onSlotClick}) => {

    const renderShape = (shape, color) => {
        switch (shape) {
            case 'circle':
                return <Circle playerColor={color} />
            case 'square':
                return <Square playerColor={color} />
            case 'triangle':
                return <Triangle playerColor={color} />
            default:
                return null
        }
    }

    const isSelectable = (index) => {
        return available_actions.hasOwnProperty('select_a_slot') &&
        available_actions['select_a_slot'].hasOwnProperty(tile_index) &&
        available_actions['select_a_slot'][tile_index].includes(index)
    }

    return (
        <div className="shapes-on-tile">
            {slots_for_shapes.map((slot, index) => (
                <div 
                    key={index} 
                    className={`slot ${isSelectable(index) ? 'selectable-slot' : ''}`}
                    onClick={() => isSelectable(index) && onSlotClick(index)}
                >
                    {slot ? renderShape(slot.shape, slot.color) : null}
                </div>
            ))}
        </div>
    )
}

export default ShapesOnTile