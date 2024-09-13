import React from 'react';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';
import Tooltip from './tooltip';
import '../stylesheets/player_HUD.css';

const ArrowIcon = ({ rotation }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style={{ transform: `rotate(${rotation}deg)` }}>
    <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
  </svg>
);

const CostGrid = ({ costs_to_recruit, costs_to_exile, player_color, available_actions, clients_color, shapes, onShapeClick }) => {
  const shapeTypes = ['circle', 'square', 'triangle'];
  const ShapeComponents = { circle: Circle, square: Square, triangle: Triangle };

  const isSelectable = (shape_type) => {
    return (
      available_actions.hasOwnProperty('select_a_shape_in_the_HUD') && available_actions['select_a_shape_in_the_HUD'].includes(shape_type) && clients_color === player_color
    )
  }

  const renderShapeComponent = (shape) => {
    const selectable = isSelectable(shape);
    const clickHandler = selectable ? () => onShapeClick(shape, player_color) : undefined;

    return React.createElement(ShapeComponents[shape], {
      playerColor: player_color,
      selectable: selectable,
      onClick: clickHandler
    })
  }

  return (
    <div className="cost-grid">
      <div className="cost-row shapes-row">
        <div className="cost-cell"> <b>Costs:</b> </div>
        {shapeTypes.map(shape => (
          <div key={`shape-${shape}`} className="cost-cell">
            {renderShapeComponent(shape)}
          </div>
        ))}
      </div>
      <div className="cost-row">
        <div className="cost-cell">
          <Tooltip text="Recruit">
            <ArrowIcon rotation={90} />
          </Tooltip>
        </div>
        {shapeTypes.map(shape => (
          <div key={`recruit-${shape}`} className="cost-cell">
            <span>{costs_to_recruit[shape]}</span>
          </div>
        ))}
      </div>
      <div className="cost-row">
        <div className="cost-cell">
          <Tooltip text="Exile">
            <ArrowIcon rotation={0} />
          </Tooltip>
        </div>
        {shapeTypes.map(shape => (
          <div key={`exile-${shape}`} className="cost-cell">
            <span>{costs_to_exile[shape]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const PlayerHUD = ({
  player_color,
  whose_turn_is_it,
  has_passed,
  clients_color,
  points,
  presence,
  stamina,
  peak_power,
  available_actions,
  onShapeClick,
  costs_to_exile,
  costs_to_recruit,
  shapes
}) => {
  const class_for_player_color = player_color === 'red' ? 'player-red' : 'player-blue';
  const active_player_class = whose_turn_is_it === player_color ? 'player-active' : '';
  return (
    <div className={`player-info ${class_for_player_color} ${active_player_class} ${has_passed ? 'player-has-passed' : ''}`}>
      <div className='points-presence-stamina-peak-power-row'>
        <div> <b>Points:</b> {points}</div>
        <div> <b>Presence:</b> {presence}</div>
        <div> <b>Peak Power:</b> {peak_power}</div>
        <div> <b>Stamina:</b> {stamina}</div>                  
      </div>
      <CostGrid 
        costs_to_recruit={costs_to_recruit} 
        costs_to_exile={costs_to_exile} 
        player_color={player_color}
        available_actions={available_actions}
        clients_color={clients_color}
        shapes={shapes}
        onShapeClick={onShapeClick}
      />
    </div>
  )
}

export default PlayerHUD;