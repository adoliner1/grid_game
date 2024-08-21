import React from 'react'
import '../stylesheets/powerup.css'
import ShapesOnPowerup from './shapes_on_powerup'

const Powerup = ({ description, clients_color, powerup_index, is_on_cooldown, available_actions, onPowerupClick, slots_for_shapes, onPowerupSlotClick, playerColorOfPowerups }) => {

    const isSelectable = () => {
        return available_actions.hasOwnProperty('select_a_powerup') &&
            available_actions['select_a_powerup'].includes(powerup_index) && clients_color === playerColorOfPowerups
    }

    const formattedDescription = description
    .replace(/\n/g, '<br><br>')
    .replace(/Ruler:/g, '<strong>Ruler:</strong>')
    .replace(/Action:/g, '<strong>Action:</strong>')
    .replace(/Reaction:/g, '<strong>Reaction:</strong>')
    .replace(/(\d+)\s+Power/g, '<strong>$1 Power</strong>')
    .replace(/start of a round/gi, '<i>start of a round</i>')
    .replace(/end of a round/gi, '<i>end of a round</i>')
    .replace(/end of the game/gi, '<i>end of the game</i>')
    .replace(/\b(burn|burns|burned)\b/gi, '<span style="color: #ff8700;">$1</span>')
    .replace(/\b(receive|receives|received)\b/gi, '<span style="color: #9f00ff;">$1</span>')
    .replace(/\b(place|places|placed|placing)\b/gi, '<span style="color: #007a9a;">$1</span>')
    .replace(/\b(produce|produces|produced|producing)\b/gi, '<span style="color: #019000;">$1</span>');

    const powerupClickHandler = isSelectable() ? onPowerupClick : undefined

    return (
        <div className={`powerup-container ${isSelectable() ? 'selectable-powerup' : ''} ${is_on_cooldown ? 'powerup-on-cooldown' : ''}`} onClick={powerupClickHandler}>
            <div className="powerup-description" dangerouslySetInnerHTML={{ __html: formattedDescription }} />
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