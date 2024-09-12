import React from 'react'
import '../stylesheets/player_HUD.css'

const PlayerHUD = ({player_color, whose_turn_is_it, has_passed, clients_color, points, presence, stamina, peak_power, available_actions, onShapeClick}) => {

    return (
        <div className={`player-info ${has_passed ? 'player-has-passed' : ''}`}>
                <div className='points-presence-stamina-peak-power-row'>
                    <div> <b>Points:</b> {points}</div>
                    <div> <b>Presence:</b> {presence}</div>
                    <div> <b>Peak Power:</b> {peak_power}</div>
                    <div> <b>Stamina:</b> {stamina}</div>                  
                </div>                 
        </div>
    )
}

export default PlayerHUD