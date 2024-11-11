import React from 'react'
import '../stylesheets/influence_tier.css'
import Tooltip from './tooltip'
import createIcon from './icons'

const InfluenceTier = ({
  tier,
  isSelectable,
  onTierClick,
  redAtThisLevel,
  blueAtThisLevel
}) => {
 
  function parseCustomMarkup(text) {
    const parts = text.split(/(\bpower\b|\binfluence\b|\bpoints?\b|\bfollowers?\b|\bacolytes?\b|\bsages?\b|\bleaders?\b|\bleader_movement\b)/gi)
    return parts.map((part, index) => {
      const lowerPart = part.toLowerCase()
      switch(lowerPart) {
        case 'power':
          return createIcon({
            type: 'power',
            tooltipText: 'Power',
            width: 16,
            height: 16,
            className: 'power-icon'
          })
        case 'influence':
          return createIcon({
            type: 'influence',
            tooltipText: 'Influence',
            width: 16,
            height: 16,
            className: 'influence-icon'
          })
        case 'point':
        case 'points':
          return createIcon({
            type: 'points',
            tooltipText: 'Points',
            width: 16,
            height: 16,
            className: 'points-icon'
          })
        case 'follower':
        case 'followers':
          return createIcon({
            type: 'follower',
            tooltipText: 'Follower',
            width: 16,
            height: 16,
            className: 'follower-icon'
          })
        case 'acolyte':
        case 'acolytes':
          return createIcon({
            type: 'acolyte',
            tooltipText: 'Acolyte',
            width: 16,
            height: 16,
            className: 'acolyte-icon'
          })
        case 'sage':
        case 'sages':
          return createIcon({
            type: 'sage',
            tooltipText: 'Sage',
            width: 16,
            height: 16,
            className: 'sage-icon'
          })
        case 'leader':
        case 'leaders':
          return createIcon({
            type: 'leader',
            tooltipText: 'Leader',
            width: 16,
            height: 16,
            className: 'leader-icon'
          })
        case 'leader_movement':
          return createIcon({
            type: 'leader_movement',
            tooltipText: 'Leader Movement',
            width: 16,
            height: 16,
            className: 'leader-movement-icon'
          })
        default:
          return part
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/__(.*?)__/g, '<i>$1</i>')  // Italic
            .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700">$1</span>')  // Burn (orange)
            .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff">$1</span>')  // Receive (purple)
            .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a">$1</span>')  // Place (blue)
            .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000">$1</span>')  // Produce (green)
            .replace(/\b(action|reaction)\b/gi, '<u>$1</u>')  // Underline action and reaction
            .replace(/\n/g, '<br>')  // New line
      }
    })
  }
 
  const getCrownClassToDetermineColor = () => {
    if (redAtThisLevel && blueAtThisLevel) return 'crown-both'
    if (redAtThisLevel) return 'crown-red'
    if (blueAtThisLevel) return 'crown-blue'
    return ''
  }

  const cooldown_clock = createIcon({
    type: 'cooldownClock',
    tooltipText: 'Once per Round',
    width: 12,
    height: 12,
    className: 'cooldown-icon'
  })

  const crown = createIcon({
    type: 'crown',
    tooltipText: 'Must be Ruler',
    width: 12,
    height: 12,
    className: `crown-icon ${getCrownClassToDetermineColor()}`
  })

  const influence_tier_meeple = createIcon({
    type: 'leader',
    tooltipText: 'Leader Must be Present',
    width: 12,
    height: 12
  })

  const Indicator = ({ color }) => createIcon({
    type: 'indicator',
    color: color,
    width: 10,
    height: 2
  })

  return (
    <div
      className={`influence-tier ${isSelectable ? 'selectable-influence-tier' : ''} ${tier.is_on_cooldown ? 'influence-tier-on-cooldown' : ''}`}
      onClick={() => isSelectable && onTierClick()}
    >
      <div className='influence-tier-indicators-and-requirements'>
          <div className="ruler-tier"> {tier.must_be_ruler ? crown : null} </div>
          <Tooltip text="Influence to Reach Tier">
            <div className="influence-requirement-at-tier">{tier.influence_to_reach_tier}</div>
          </Tooltip>
          <div className="has_a_cooldown">{tier.has_a_cooldown ? cooldown_clock : null}</div>
          <div className="leader_must_be_present">{tier.leader_must_be_present ? influence_tier_meeple : null} </div>
          <div className="player-indicators-for-influence-tiers">
            {redAtThisLevel && <Indicator color="red" />}
            {blueAtThisLevel && <Indicator color="blue" />}
          </div>
      </div>
      <div className="tier-description">
        {parseCustomMarkup(tier.description).map((part, index) =>
          typeof part === 'string' ?
            <span key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part }} /> :
            React.cloneElement(part, { key: `icon-${index}` })
        )}
      </div>
    </div>
  )
}

export default InfluenceTier