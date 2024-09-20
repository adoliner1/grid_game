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

    const meeple = (color) => createIcon({
        type: 'meeple',
        tooltipText: `${color.charAt(0).toUpperCase() + color.slice(1)} Leader`,
        color: color,
        width: 20,
        height: 24
    });

    const crownIcon = createIcon({
        type: 'crown',
        tooltipText: 'Influence Needed to Rule',
        width: 24,
        height: 24,
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
        const parts = text.split(/(\bpower\b|\binfluence\b|\bpoints\b)/gi);
        return parts.map((part, index) => {
          const lowerPart = part.toLowerCase();
          if (lowerPart === 'power') {
            return createIcon({
              type: 'power',
              tooltipText: 'Power',
              width: 14,
              height: 14,
              className: 'power-icon'
            });
          }
          if (lowerPart === 'influence') {
            return createIcon({
              type: 'influence',
              tooltipText: 'Influence',
              width: 14,
              height: 14,
              className: 'influence-icon'
            });
          }
          if (lowerPart === 'points') {
            return createIcon({
                type: 'points',
                tooltipText: `Points`,
                width: 16,
                height: 16,
                className: 'points-icon'
            });
          }
          return part
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/__(.*?)__/g, '<i>$1</i>')  // Italic
            .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700;">$1</span>')  // Burn (orange)
            .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff;">$1</span>')  // Receive (purple)
            .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a;">$1</span>')  // Place (blue)
            .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000;">$1</span>')  // Produce (green)
            .replace(/\b(action|reaction)\b/gi, '<u>$1</u>')  // Underline action and reaction
            .replace(/\n/g, '<br>')  // New line
        });
    }

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${is_on_cooldown ? 'tile-on-cooldown' : ''}`} onClick={tileClickHandler}>
            <div className="tile-header">
                <div className={`ruler-crown-in-header ${ruler ? `ruler-crown-${ruler}` : ''}`}>
                    {crownIcon}
                    {minimum_influence_to_rule}
                </div>
                <div className='red-leader-here'>{leaders_here.red && meeple('red')} </div>
                <h3 className='tile-name'>{name}</h3>
                <div className='blue-leader-here'>{leaders_here.blue && meeple('blue')} </div>
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
    )
}

export default Tile