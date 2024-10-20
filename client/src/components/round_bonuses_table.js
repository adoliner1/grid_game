import React from 'react';
import createIcon from './icons';
import Tooltip from './tooltip';
import '../stylesheets/round_bonuses_table.css'

const RoundBonusesTable = ({ gameState }) => {
  const totalRounds = Math.max(gameState.scorer_bonuses.length, gameState.income_bonuses.length);

  const rowIcon = createIcon({ type: 'row', width: 24, height: 8 });
  const columnIcon = createIcon({ type: 'column', width: 8, height: 24 });
  const diagonalIcon = createIcon({ type: 'diagonal', width: 24, height: 24 });
  const presenceIcon = createIcon({ type: 'presence', width: 16, height: 16 });
  const peakInfluenceIcon = createIcon({type: 'peakInfluence', width: 24, height: 24});
  const pointsIcon = createIcon({ type: 'points', width: 16, height: 16 });
  const powerIcon = createIcon({ type: 'power', width: 16, height: 16 });
  const ruledTilesIcon = createIcon({ type: 'crown', width: 16, height: 16 });
  const inCornerIcon = createIcon({ type: 'inCorner', width: 16, height: 16 });
  const connectedChainIcon = createIcon({ type: 'connectedChain', width: 16, height: 16 });
  const leaderIcon = createIcon({ type: 'leader', width: 16, height: 16 });
  const leaderMovementIcon = createIcon({ type: 'leader_movement', width: 16, height: 16 });

  const bonusDescriptions = {
    "12 points ruled-tile row": "If you rule all 3 tiles in a row, +12 points",
    "10 points ruled-tile column": "If you rule all 3 tiles in a column, +10 points",
    "16 points ruled-tile diagonal": "If you rule all 3 tiles in a diagonal, +16 points",
    "2 points ruled-tile": "Gain 2 points for each tile you rule",
    "power presence": "Gain power equal to your presence",
    "1/2 power peak-influence": "Gain power equal to your peak influence/2 (round down)",
    "2 power ruled-tile longest-chain": "Gain power equal to the length*2 of your longest connected chain of ruled tiles",
    "3 points ruled-tile longest-chain": "Gain points equal to the length*3 of your longest connected chain of ruled tiles",
    "points presence": "Gain points equal to your presence",
    "1/2 points peak-influence": "Gain points equal to your peak influence/2 (round down)",
    "3 power ruled-tile corner": "Gain 3 power for each corner tile you rule",
    "7 power ruled-tile row": "If you rule all 3 tiles in a row, gain 7 power",
    "7 power ruled-tile column": "If you rule all 3 tiles in a column, gain 7 power",
    "10 power ruled-tile diagonal": "If you rule all 3 tiles in a diagonal, gain 10 power",
    "2 power ruled-tile": "Gain 2 power for each tile you rule",
    "5 points ruled-tile corner": "Gain 5 points for each corner tile you rule",
    "25 points ruled-tile corner": "Gain 25 points if you rule all 4 corner tiles",
    "1/2 leader-movement presence": "Gain leader movement equal to your presence/2 (round down)",
    "1/3 leader-movement peak-influence": "Gain leader movement equal to your peak influence/3 (round down)",
    "2 leader-movement ruled-tile corner": "Gain 2 leader movement for each corner tile you rule"
  };

  const getSubtypeIcon = (subtype) => {
    switch (subtype.toLowerCase()) {
      case 'row': return rowIcon;
      case 'column': return columnIcon;
      case 'diagonal': return diagonalIcon;
      case 'ruled-tile': return ruledTilesIcon;
      case 'corner': return inCornerIcon;
      case 'leader': return leaderIcon;
      case 'presence': return presenceIcon;
      case 'peak-influence': return peakInfluenceIcon;
      case 'longest-chain': return connectedChainIcon;
      case 'leader-movement': return leaderMovementIcon;
      default: return null;
    }
  };

  const parseBonus = (bonusText) => {
    if (!bonusText) return ['N/A'];

    const parts = bonusText.split(/(\s+)/);
    const parsedParts = parts.map((part, index) => {
      if (part.match(/^\d+(\.\d+)?$/)) {
        return <span key={index} className="font-bold">{part}</span>;
      } else if (part.toLowerCase() === 'points') {
        return <span key={index} className="bonus-icon">{pointsIcon}</span>;
      } else if (part.toLowerCase() === 'power') {
        return <span key={index} className="bonus-icon">{powerIcon}</span>;
      } else if (part.toLowerCase() === 'leader-movement') {
        return <span key={index} className="bonus-icon">{leaderMovementIcon}</span>;
      } else {
        const subtypeIcon = getSubtypeIcon(part);
        return subtypeIcon ? <span key={index} className="bonus-icon">{subtypeIcon}</span> : part;
      }
    });

    return (
      <Tooltip text={bonusDescriptions[bonusText] || bonusText}>
        <span className="bonus-content">{parsedParts}</span>
      </Tooltip>
    );
  };

  return (
    <table className="round-bonuses-table">
      <thead>
        <tr>
          <th>End of Round Base Income</th>
          <th>End of Round Bonus Income</th>
          <th>End of Round Bonus Points</th>
        </tr>
      </thead>
      <tbody>
        {[...Array(totalRounds)].map((_, index) => (
          <tr key={index} className={index === gameState.round ? 'current-round' : ''}>
            <td>
              {index < totalRounds - 1 ? gameState.power_given_at_start_of_round[index] : ''}
            </td>
            <td>
              {index < totalRounds - 1 ? parseBonus(gameState.income_bonuses[index]) : ''}
            </td>
            <td>{parseBonus(gameState.scorer_bonuses[index])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default RoundBonusesTable;