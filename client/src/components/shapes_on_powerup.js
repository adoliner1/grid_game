import React from 'react'
import Circle from './shapes/circle'
import Square from './shapes/square'
import Triangle from './shapes/triangle'
import '../stylesheets/shapes_on_powerup.css'

const ShapesOnPowerup = ({ slots_for_shapes, powerup_index, available_actions, onPowerupSlotClick, playerColor }) => {

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
        return available_actions.hasOwnProperty('select_a_slot_on_a_powerup') &&
            available_actions['select_a_slot_on_a_powerup'][playerColor].hasOwnProperty(powerup_index) &&
            available_actions['select_a_slot_on_a_powerup'][playerColor][powerup_index].includes(index)
    }

    return (
        <div className="shapes-on-powerup">
            {slots_for_shapes.map((slot, index) => (
                <div
                    key={index}
                    className={`slot ${isSelectable(index) ? 'selectable-slot' : ''}`}
                    onClick={() => isSelectable(index) && onPowerupSlotClick(index)}
                >
                    {slot ? renderShape(slot.shape, slot.color) : null}
                </div>
            ))}
        </div>
    )
}

export default ShapesOnPowerup
