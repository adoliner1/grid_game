import React from 'react';
import createIcon from './icons';
import Tooltip from './tooltip';
import '../stylesheets/round_bonuses_table.css'

const RoundBonusesTable = ({ gameState }) => {
  const totalRounds = Math.max(gameState.scorer_bonuses.length, gameState.income_bonuses.length);

  const rowIcon = createIcon({ type: 'row', width: 24, height: 8 });
  const columnIcon = createIcon({ type: 'column', width: 8, height: 24 });
  const presenceIcon = createIcon({ type: 'presence', width: 16, height: 16 });
  const peakInfluenceIcon = createIcon({type: 'peakInfluence', width: 24, height: 24});
  const pointsIcon = createIcon({ type: 'points', width: 16, height: 16 });
  const powerIcon = createIcon({ type: 'power', width: 16, height: 16 });
  const ruledTilesIcon = createIcon({ type: 'ruledTiles', width: 48, height: 24 });
  const inCornerIcon = createIcon({ type: 'inCorner', width: 16, height: 16 });
  const connectedChainIcon = createIcon({ type: 'connectedChain', width: 16, height: 16 });

  const bonusDescriptions = {
    "10 points row": "If you rule all 3 tiles in a row, +10 points",
    "10 points column": "If you rule all 3 tiles in a column, +10 points",
    "2 points tile": "Gain 2 points for each tile you rule",
    "1/2 power presence": "Gain power equal to your presence/2 (round down)",
    "1/2 power peak-influence": "Gain power equal to your peak influence/2 (round down)",
    "2 power longest-chain": "Gain power equal to the length*2 of your longest connected chain of ruled tiles",
    "3 points longest-chain": "Gain points equal to the length*3 of your longest connected chain of ruled tiles",
    "points presence": "Gain points equal to your presence",
    "points peak-influence": "Gain points equal to your peak influence",
    "3 power corner": "Gain 3 power if your leader is on a corner tile",
    "5 power row": "If you rule all 3 tiles in a row, gain 5 power",
    "5 power column": "If you rule all 3 tiles in a column, gain 5 power",
    "power tile": "Gain 1 power for each tile you rule",
    "5 points corner": "Gain 5 points if your leader is on a corner tile"
  };

  const getSubtypeIcon = (subtype) => {
    switch (subtype.toLowerCase()) {
      case 'row': return rowIcon;
      case 'column': return columnIcon;
      case 'tile': return ruledTilesIcon;
      case 'corner': return inCornerIcon;
      case 'presence': return presenceIcon;
      case 'peak-influence': return peakInfluenceIcon;
      case 'longest-chain': return connectedChainIcon;
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
          <th>Base Power Income</th>
          <th>End of Round Income</th>
          <th>End of Round Scoring </th>
        </tr>
      </thead>
      <tbody>
        {[...Array(totalRounds)].map((_, index) => (
          <tr key={index} className={index === gameState.round ? 'current-round' : ''}>
            <td>{gameState.power_given_at_start_of_round[index]}</td>
            <td>{parseBonus(gameState.income_bonuses[index])}</td>
            <td>{parseBonus(gameState.scorer_bonuses[index])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default RoundBonusesTable;