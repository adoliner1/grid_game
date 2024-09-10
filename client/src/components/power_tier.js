import React from 'react';
import '../stylesheets/power_tier.css'

const PowerTier = ({
  tier,
  isSelectable,
  onTierClick,
  redAtThisLevel,
  blueAtThisLevel
}) => {
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
 
  const getCrownClass = () => {
    if (redAtThisLevel && blueAtThisLevel) return 'crown-both';
    if (redAtThisLevel) return 'crown-red';
    if (blueAtThisLevel) return 'crown-blue';
    return ''
  }

  const cooldown_clock = (
    <svg className="cooldown-icon" viewBox="0 0 24 24" width="12" height="12">
      <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="M12 6v6l4 2" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )

  const crown = (
    <svg className={`crown-icon ${getCrownClass()}`} viewBox="0 0 24 24" width="12" height="12">
        <path fill="currentColor" d="M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5M19 19C19 19.6 18.6 20 18 20H6C5.4 20 5 19.6 5 19V18H19V19Z" />
    </svg>
  )

  const Indicator = ({ color }) => (
    <svg width="10" height="2" viewBox="0 0 10 2">
      <line x1="0" y1="1" x2="10" y2="1" stroke={color} strokeWidth="2" />
    </svg>
  )

  return (
    <div
      className={`power-tier ${isSelectable ? 'selectable-power-tier' : ''} ${tier.is_on_cooldown ? 'power-tier-on-cooldown' : ''}`}
      onClick={() => isSelectable && onTierClick()}
    >
      <div className='power-tier-indicators-and-requirements'>
          <div className="ruler-tier"> {tier.must_be_ruler ? crown : null} </div>
          <div className="power-requirement-at-tier">{tier.power_to_reach_tier}</div>
          <div className="has_a_cooldown">{tier.has_a_cooldown ? cooldown_clock : null}</div>
          <div className="player-indicators-for-power-tiers">
            {redAtThisLevel && <Indicator color="red" />}
            {blueAtThisLevel && <Indicator color="blue" />}
          </div>
      </div>
      <div className="tier-description" dangerouslySetInnerHTML={{ __html: parseCustomMarkup(tier.description) }}></div>
    </div>
  );
};

export default PowerTier;