import React from 'react';
import Follower from './disciples/follower';
import Acolyte from './disciples/acolyte';
import Sage from './disciples/sage';
import Tooltip from './tooltip';
import createIcon from './icons';
import '../stylesheets/player_HUD.css';

const ArrowIcon = ({ rotation }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style={{ transform: `rotate(${rotation}deg)` }}>
    <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
  </svg>
)

const CostGrid = ({ costs_to_recruit, costs_to_exile, player_color, available_actions, clients_color, onDiscipleClick, recruiting_range, exiling_range }) => {
  const disciple_types = ['follower', 'acolyte', 'sage'];
  const DiscipleComponents = { follower: Follower, acolyte: Acolyte, sage: Sage };
  const rangeIcon = createIcon({ type: 'range', tooltipText: 'Range', width: 18, height: 18 });

  const isSelectable = (disciple_type) => {
    return (
      available_actions.hasOwnProperty('select_a_disciple_in_the_HUD') && 
      available_actions['select_a_disciple_in_the_HUD'].includes(disciple_type) && 
      clients_color === player_color
    )
  }

  const renderDiscipleComponent = (disciple) => {
    const selectable = isSelectable(disciple);
    const clickHandler = selectable ? () => onDiscipleClick(disciple, player_color) : undefined;

    return React.createElement(DiscipleComponents[disciple], {
      playerColor: player_color,
      selectable: selectable,
      onClick: clickHandler
    })
  }

  return (
    <div className="cost-grid">
      <div className="cost-row">
        <div className="cost-cell"> </div>
        <div className="cost-cell"> {rangeIcon} </div>
        {disciple_types.map(disciple => (
          <div key={`disciple-${disciple}`} className="cost-cell">
            {renderDiscipleComponent(disciple)}
          </div>
        ))}
      </div>
      <div className="cost-row">
        <div className="cost-cell">
          <Tooltip text="Power to Recruit">
            <ArrowIcon rotation={90} />
          </Tooltip>
        </div>
        <div className="cost-cell">
          <span><b>{recruiting_range}</b></span>
        </div>
        {disciple_types.map(disciple => (
          <div key={`recruit-${disciple}`} className="cost-cell">
            <span><b>{costs_to_recruit[disciple]}</b></span>
          </div>
        ))}
      </div>
      <div className="cost-row">
        <div className="cost-cell">
          <Tooltip text="Power to Exile">
            <ArrowIcon rotation={0} />
          </Tooltip>
        </div>
        <div className="cost-cell">
          <span><b>{exiling_range}</b></span>
        </div>
        {disciple_types.map(disciple => (
          <div key={`exile-${disciple}`} className="cost-cell">
            <span><b>{costs_to_exile[disciple]}</b></span>
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
  power,
  peak_influence,
  available_actions,
  onDiscipleClick,
  costs_to_exile,
  costs_to_recruit,
  recruiting_range,
  exiling_range,
}) => {
  const class_for_player_color = player_color === 'red' ? 'player-red' : 'player-blue';
  const active_player_class = whose_turn_is_it === player_color ? 'player-active' : '';
  const class_to_show_border_by_client_color = player_color === clients_color ? 'player-is-this-color' : ''; 

  const pointsIcon = createIcon({ type: 'points', tooltipText: 'Points', width: 18, height: 18 });
  const presenceIcon = createIcon({ type: 'presence', tooltipText: 'Presence', width: 18, height: 18 });
  const peakInfluenceIcon = createIcon({ type: 'peakInfluence', tooltipText: 'Peak Influence', width: 18, height: 18 });
  const powerIcon = createIcon({ type: 'power', tooltipText: 'Power', width: 18, height: 18 });

  return (
    <div className={`player-info ${class_for_player_color} ${class_to_show_border_by_client_color} ${active_player_class} ${has_passed ? 'player-has-passed' : ''}`}>
      <div className='points-presence-power-peak-influence-row'>
        <div className="icon-value-pair">
          {pointsIcon} : 
          <span>{points}</span>
        </div>
        <div className="icon-value-pair">
          {presenceIcon} : 
          <span>{presence}</span>
        </div>
        <div className="icon-value-pair">
          {peakInfluenceIcon} : 
          <span>{peak_influence}</span>
        </div>
        <div className="icon-value-pair">
          {powerIcon} : 
          <span>{power}</span>
        </div>
      </div>
      <CostGrid
        costs_to_recruit={costs_to_recruit}
        costs_to_exile={costs_to_exile}
        recruiting_range={recruiting_range}
        exiling_range={exiling_range}
        player_color={player_color}
        available_actions={available_actions}
        clients_color={clients_color}
        onDiscipleClick={onDiscipleClick}
      />
    </div>
  )
}

export default PlayerHUD 