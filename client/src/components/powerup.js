import React from 'react'
import '../stylesheets/powerup.css'
import ShapesOnPowerup from './shapes_on_powerup'

const Powerup = ({ description, powerup_index, available_actions, onPowerupClick, slots_for_shapes, onPowerupSlotClick, playerColorOfPowerups }) => {

    const isSelectable = () => {
        return available_actions.hasOwnProperty('select_a_powerup') &&
            available_actions['select_a_powerup'].includes(powerup_index)
    }

    const powerupClickHandler = isSelectable() ? onPowerupClick : undefined

    return (
        <div className={`powerup-container ${isSelectable() ? 'selectable-powerup' : ''}`} onClick={powerupClickHandler}>
            <div className="powerup-description">
                {description}
            </div>
            <ShapesOnPowerup
                slots_for_shapes={slots_for_shapes}
                powerup_index={powerup_index}
                available_actions={available_actions}
                onPowerupSlotClick={onPowerupSlotClick}
                playerColor={playerColorOfPowerups}
            />
        </div>
    )
}

export default Powerup