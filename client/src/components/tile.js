import React from 'react'
import '../stylesheets/tile.css'
import DisciplesOnTile from './disciples_on_tile'
import InfluenceTier from './influence_tier'
import Tooltip from './tooltip';
import createIcon from './icons';

const Tile = ({
    name,
    minimum_influence_to_rule,
    type,
    description,
    influence_tiers,
    red_influence,
    blue_influence,
    is_on_cooldown,
    slots_for_disciples,
    tile_index,
    leaders_here,
    ruler,
    available_actions,
    onTileClick,
    onSlotClick,
    onInfluenceTierClick,
}) => {

    const leader_icon = (color) => createIcon({
        type: 'leader',
        tooltipText: `${color.charAt(0).toUpperCase() + color.slice(1)} Leader`,
        color: color,
        width: 20,
        height: 24
    });

    const crownIcon = createIcon({
        type: 'crown',
        tooltipText: 'Influence Needed to Rule',
        width: 22,
        height: 22,
        className: 'crown-icon'
    });

    const influenceIcon = (color) => createIcon({
        type: 'influence',
        tooltipText: `${color.charAt(0).toUpperCase() + color.slice(1)} Influence`,
        color: color,
        width: 16,
        height: 16,
        className: 'influence-icon'
    });

    const isSelectableTier = (tier_index) => {
        return available_actions.hasOwnProperty('select_a_tier') &&
          available_actions['select_a_tier'].hasOwnProperty(tile_index) &&
          available_actions['select_a_tier'][tile_index].includes(tier_index);
    };

    const isSelectable = () => {
        return available_actions.hasOwnProperty('select_a_tile') && available_actions['select_a_tile'].includes(tile_index)
    }

    const tileClickHandler = isSelectable() ? onTileClick : undefined

    function parseCustomMarkup(text) {
        const parts = text.split(/(\bpower\b|\binfluence\b|\bpoints?\b|\bfollowers?\b|\bacolytes?\b|\bsages?\b|\bleaders?\b)/gi);
        return parts.map((part, index) => {
          const lowerPart = part.toLowerCase();
          switch(lowerPart) {
            case 'power':
              return createIcon({
                type: 'power',
                tooltipText: 'Power',
                width: 16,
                height: 16,
                className: 'power-icon'
              });
            case 'influence':
              return createIcon({
                type: 'influence',
                tooltipText: 'Influence',
                width: 16,
                height: 16,
                className: 'influence-icon'
              });
            case 'point':
            case 'points':
              return createIcon({
                type: 'points',
                tooltipText: 'Points',
                width: 16,
                height: 16,
                className: 'points-icon'
              });
            case 'follower':
            case 'followers':
              return createIcon({
                type: 'follower',
                tooltipText: 'Follower',
                width: 16,
                height: 16,
                className: 'follower-icon'
              });
            case 'acolyte':
            case 'acolytes':
              return createIcon({
                type: 'acolyte',
                tooltipText: 'Acolyte',
                width: 16,
                height: 16,
                className: 'acolyte-icon'
              });
            case 'sage':
            case 'sages':
              return createIcon({
                type: 'sage',
                tooltipText: 'Sage',
                width: 16,
                height: 16,
                className: 'sage-icon'
              });
            case 'leader':
            case 'leaders':
              return createIcon({
                type: 'leader',
                tooltipText: 'Leader',
                width: 16,
                height: 16,
                className: 'leader-icon'
              });
            default:
              return part
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/__(.*?)__/g, '<i>$1</i>')
                .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700;">$1</span>')
                .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff;">$1</span>')
                .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a;">$1</span>')
                .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000;">$1</span>')
                .replace(/\b(action|reaction)\b/gi, '<u>$1</u>')
                .replace(/\n/g, '<br>')
          }
        });
    }

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'}`} onClick={tileClickHandler}>
            <div className="tile-content">
                <div className="tile-header">
                    <div className={`ruler-crown-in-header ${ruler ? `ruler-crown-${ruler}` : ''}`}>
                        {crownIcon}
                        {minimum_influence_to_rule}
                    </div>
                    <div className='red-leader-here'>{leaders_here.red && leader_icon('red')} </div>
                    <h3 className='tile-name'>{name}</h3>
                    <div className='blue-leader-here'>{leaders_here.blue && leader_icon('blue')} </div>
                    <span className="tile-type">{type}</span>
                </div>
                {description && (
                    <div className="tile-description">
                        {parseCustomMarkup(description).map((part, index) =>
                            typeof part === 'string' ?
                                <span key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part }} /> :
                                React.cloneElement(part, { key: `icon-${index}` })
                        )}
                    </div>
                )}
                <div className="influence-tiers">
                    {influence_tiers.map((tier, tier_index) => (
                        <InfluenceTier
                            key={tier_index}
                            tier={tier}
                            tile_index={tile_index}
                            isSelectable={isSelectableTier(tier_index)}
                            onTierClick={() => onInfluenceTierClick(tier_index)}
                            redAtThisLevel={tier.must_be_ruler ? ruler === 'red' && red_influence >= tier.influence_to_reach_tier : red_influence >= tier.influence_to_reach_tier}
                            blueAtThisLevel={tier.must_be_ruler ? ruler === 'blue' && blue_influence >= tier.influence_to_reach_tier : blue_influence >= tier.influence_to_reach_tier}
                        />
                    ))}
                </div>
            </div>
            <div className="tile-bottom">
                <div className="influence-per-player">
                    <p className='red-influence'>{influenceIcon('red')} {red_influence}</p>
                    <p className='blue-influence'>{influenceIcon('blue')} {blue_influence}</p>
                </div>
                    <DisciplesOnTile 
                        slots_for_disciples={slots_for_disciples} 
                        tile_index={tile_index}
                        available_actions={available_actions}
                        onSlotClick={onSlotClick}
                    />
            </div>
        </div>
    )
}

export default Tile