import React from 'react';
import { Tooltip } from '@/components/ui/tooltip'; // Assuming you have a Tooltip component

const CompletedColumn = () => (
  <Tooltip text="Per column you rule">
    <svg width="24" height="24" viewBox="0 0 24 24">
      <rect x="9" y="2" width="6" height="6" />
      <rect x="9" y="9" width="6" height="6" />
      <rect x="9" y="16" width="6" height="6" />
    </svg>
  </Tooltip>
);

const CompletedRow = () => (
  <Tooltip text="Per row you rule">
    <svg width="24" height="24" viewBox="0 0 24 24">
      <rect x="2" y="9" width="6" height="6" />
      <rect x="9" y="9" width="6" height="6" />
      <rect x="16" y="9" width="6" height="6" />
    </svg>
  </Tooltip>
);

const CornerHighlight = () => (
  <Tooltip text="If your leader is in a corner">
    <svg width="24" height="24" viewBox="0 0 24 24">
      <rect x="2" y="2" width="6" height="6" opacity="0.8" />
      <rect x="9" y="2" width="6" height="6" opacity="0.3" />
      <rect x="16" y="2" width="6" height="6" opacity="0.8" />
      <rect x="2" y="9" width="6" height="6" opacity="0.3" />
      <rect x="9" y="9" width="6" height="6" opacity="0.3" />
      <rect x="16" y="9" width="6" height="6" opacity="0.3" />
      <rect x="2" y="16" width="6" height="6" opacity="0.8" />
      <rect x="9" y="16" width="6" height="6" opacity="0.3" />
      <rect x="16" y="16" width="6" height="6" opacity="0.8" />
    </svg>
  </Tooltip>
);

const RoundBonusesTable = ({ gameState }) => {
  const totalRounds = Math.max(gameState.scorer_bonuses.length, gameState.income_bonuses.length);
  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="bg-gray-100">
          <th className="border p-2">Round</th>
          <th className="border p-2">Income Bonus</th>
          <th className="border p-2">Scoring Bonus</th>
        </tr>
      </thead>
      <tbody>
        {[...Array(totalRounds)].map((_, index) => (
          <tr key={index} className={index === gameState.round ? 'bg-yellow-100' : ''}>
            <td className="border p-2 font-bold">{index + 1}</td>
            <td className="border p-2">{gameState.income_bonuses[index] || 'N/A'}</td>
            <td className="border p-2">{gameState.scorer_bonuses[index] || 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const Stamina = (color) => (
  <Tooltip text={`Stamina`}>
      <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M0 0h512v512H0z"/>
      </svg>
  </Tooltip> )

export default RoundBonusesTable;
export { meeple, CompletedColumn, CompletedRow, CornerHighlight };


