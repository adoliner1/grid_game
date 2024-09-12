import React from 'react'
import '../stylesheets/tile.css'
import ShapesOnTile from './shapes_on_tile'
import PowerTier from './power_tier'

const Tile = ({
    name,
    minimum_power_to_rule,
    type,
    description,
    power_tiers,
    red_power,
    blue_power,
    is_on_cooldown,
    slots_for_shapes,
    tile_index,
    location_of_leaders,
    ruler,
    available_actions,
    onTileClick,
    onSlotClick,
    onPowerTierClick,
}) => {

    const meeple = (color) => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill={color}>
            <path d="M12 2C8.7 2 6 4.7 6 8c0 1.3.5 2.5 1.3 3.5l-.6 3.1C6.4 15.6 7 17 8 17h8c1 0 1.6-1.4 1.3-2.4l-.6-3.1C17.5 10.5 18 9.3 18 8c0-3.3-2.7-6-6-6z"/>
        </svg>
    );

    const isSelectableTier = (tier_index) => {
        console.log(available_actions)
        return available_actions.hasOwnProperty('select_a_tier') &&
          available_actions['select_a_tier'].hasOwnProperty(tile_index) &&
          available_actions['select_a_tier'][tile_index].includes(tier_index);
      };

    const isSelectable = () => {
            return available_actions.hasOwnProperty('select_a_tile') && available_actions['select_a_tile'].includes(tile_index)
    }

    const tileClickHandler = isSelectable() ? onTileClick : undefined

    function parseCustomMarkup(text) {
        return text
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
          .replace(/__(.*?)__/g, '<i>$1</i>')  // Italic
          .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700;">$1</span>')  // Burn (orange)
          .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff;">$1</span>')  // Receive (purple)
          .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a;">$1</span>')  // Place (blue)
          .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000;">$1</span>')  // Produce (green)
          .replace(/\b(action|reaction)\b/gi, '<u>$1</u>')  // Underline action and reaction
          .replace(/\n/g, '<br><br>')  // New line
      }

    return (
        <div className={`${isSelectable() ? 'tile selectable-tile' : 'tile'} ${is_on_cooldown ? 'tile-on-cooldown' : ''}`} onClick={tileClickHandler}>
        <div className="tile-header">
            <div className={`ruler-crown-in-header ${ruler ? `ruler-crown-${ruler}` : ''}`}>
                <svg className="crown-icon" viewBox="0 0 24 24" width="24" height="24">
                    <path fill="currentColor" d="M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5M19 19C19 19.6 18.6 20 18 20H6C5.4 20 5 19.6 5 19V18H19V19Z" />
                </svg>
                {minimum_power_to_rule}
            </div>
            <div className='red-leader-here'>{location_of_leaders.red === tile_index && meeple('red')} </div>
            <h3 className='tile-name'>{name}</h3>
            <div className='blue-leader-here'>{location_of_leaders.blue === tile_index && meeple('blue')} </div>
            <span className="tile-type">{type}</span>
        </div>
            {description && (<p className="tile-description" dangerouslySetInnerHTML={{ __html: parseCustomMarkup(description) }}></p>)}
            <div className="power-tiers">
                {power_tiers.map((tier, tier_index) => (
                    <PowerTier
                        key={tier_index}
                        tier={tier}
                        tile_index={tile_index}
                        isSelectable={isSelectableTier(tier_index)}
                        onTierClick={() => onPowerTierClick(tier_index)}
                        redAtThisLevel={tier.must_be_ruler ? ruler === 'red' && red_power >= tier.power_to_reach_tier : red_power >= tier.power_to_reach_tier}
                        blueAtThisLevel={tier.must_be_ruler ? ruler === 'blue' && blue_power >= tier.power_to_reach_tier : blue_power >= tier.power_to_reach_tier}
                    />
                ))}
             </div>
            <div className="power-per-player">
                <p className='red-power'> Red Power: {red_power} </p>
                <p className='blue-power'> Blue Power: {blue_power} </p>
            </div>
            <ShapesOnTile 
                slots_for_shapes={slots_for_shapes} 
                tile_index={tile_index}
                available_actions={available_actions}
                onSlotClick={onSlotClick}
            />
        </div>
    )
}

export default Tile