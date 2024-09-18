import React from 'react';
import Tooltip from './tooltip';

const iconPaths = {
  meeple: "M12 2C8.7 2 6 4.7 6 8c0 1.3.5 2.5 1.3 3.5l-.6 3.1C6.4 15.6 7 17 8 17h8c1 0 1.6-1.4 1.3-2.4l-.6-3.1C17.5 10.5 18 9.3 18 8c0-3.3-2.7-6-6-6z",
  crown: "M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5M19 19C19 19.6 18.6 20 18 20H6C5.4 20 5 19.6 5 19V18H19V19Z",
  presence: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
  peakPresence: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    peak: "M1 1h22"
  },
  row: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    highlight: "M2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6z"
  },
  column: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    highlight: "M9 2h6v6H9zM9 9h6v6H9zM9 16h6v6H9z"
  },
  inCorner: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    highlight: "M2 2h6v6H2zM16 2h6v6h-6zM2 16h6v6H2zM16 16h6v6h-6z"
  },
  cooldownClock: {
    circle: { cx: 12, cy: 12, r: 10 },
    path: "M12 6v6l4 2"
  },
  power: "M256 28l-32 128c-32-16-64-48-96-96 0 48 0 96 32 128-32 17-64 0-96-32 0 32 0 80 48 112-32 16-64 0-80-32 0 48 16 96 48 128-16 16-48 0-64-16 0 64 48 112 112 144h76.8l16.7-68.6-17.2-86.1-97.9 5s20.3-75.2 34.9-103.7c5-9.6 7.2-18 20-18.3 11.3 0 20.4 9.8 20.4 21.9 0 12-9.1 21.8-20.4 21.8-2.3 0-4.6-.5-6.6-1.3l-5.1 46.8c29.6-8.9 56.9-18.8 84-30.9 0-.1-.1-.2-.1-.3-6.2-8.8-10.4-21.5-10.4-35.7 0-14.1 4.1-26.8 10.4-35.7 6.1-8.9 14.1-13.7 22.5-13.7 8.5 0 16.5 4.8 22.6 13.7 6.2 8.9 10.2 21.6 10.2 35.7 0 14.2-4 26.9-10.2 35.7-.1.3-.5.7-.6.9 27.3 12.1 56.1 20.6 84.3 30.3l-5-46.8c-2.2.8-4.3 1.3-6.7 1.3-11.2 0-20.3-9.8-20.3-21.8 0-12.1 9.1-21.9 20.3-21.9 12.8.3 15.2 8.7 20 18.3 14.8 28.5 35 103.7 35 103.7l-97.9-5-17.2 86.1 16.7 68.6H384c64-32 112-80 112-144-16 16-48 32-64 16 32-32 48-80 48-128-16 32-48 48-80 32 48-32 48-80 48-112-32 32-64 48-96 32 32-32 32-80 32-128-32 48-64 80-96 96z",
  indicator: { x1: 0, y1: 1, x2: 10, y2: 1 },
  influence: "M329.8 235.69l62.83-82.71 42.86 32.56-62.83 82.75zm-12.86-9.53l66.81-88-45-34.15-66.81 88zm-27.48-97.78l-19.3 39.57 57-75-42.51-32.3-36.24 47.71zm-20.74-73.24l-46.64-35.43-42 55.31 53.67 26.17zm107 235.52l-139-102.71-9.92.91 4.56 2 62.16 138.43-16.52 2.25-57.68-128.5-40-17.7-4-30.84 39.41 19.42 36.36-3.33 17-34.83-110.9-54.09-80.68 112.51L177.6 346.67l-22.7 145.62H341V372.62l35.29-48.93L387 275.77z",
  peakInfluence: {
    influence: "M329.8 235.69l62.83-82.71 42.86 32.56-62.83 82.75zm-12.86-9.53l66.81-88-45-34.15-66.81 88zm-27.48-97.78l-19.3 39.57 57-75-42.51-32.3-36.24 47.71zm-20.74-73.24l-46.64-35.43-42 55.31 53.67 26.17zm107 235.52l-139-102.71-9.92.91 4.56 2 62.16 138.43-16.52 2.25-57.68-128.5-40-17.7-4-30.84 39.41 19.42 36.36-3.33 17-34.83-110.9-54.09-80.68 112.51L177.6 346.67l-22.7 145.62H341V372.62l35.29-48.93L387 275.77z",
    peak: "M10 10H502"
  },
  points: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
  connectedChain: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    highlight: "M2 2h6v6H2zM9 2h6v6H9zM9 9h6v6H9zM9 16h6v6H9z"
  },
  ruledTiles: {
    grid: "M2 2h6v6H2zM9 2h6v6H9zM16 2h6v6h-6zM2 9h6v6H2zM9 9h6v6H9zM16 9h6v6h-6zM2 16h6v6H2zM9 16h6v6H9zM16 16h6v6h-6z",
    crown: "M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5M19 19C19 19.6 18.6 20 18 20H6C5.4 20 5 19.6 5 19V18H19V19Z"
  }
};

const createIcon = ({ type, tooltipText, color, width = 24, height = 24, className = '' }) => {
  let viewBox = "0 0 24 24";
  switch (type) {
    case 'indicator':
      viewBox = "0 0 10 2";
      break;
    case 'influence':
    case 'peakInfluence':
      viewBox = "0 0 512 512";
      break;
    case 'power':
      viewBox = "0 0 512 512";
      break;
    case 'ruledTiles':
      viewBox = "0 0 48 24";
      break;
  }

  const svgProps = {
    width: type === 'ruledTiles' ? 48 : width,
    height,
    viewBox,
    className: `icon ${className}`,
  };

  let iconContent;
  switch (type) {
    case 'meeple':
    case 'crown':
    case 'influence':
    case 'points':
    case 'power':
      iconContent = <path d={iconPaths[type]} fill={color || 'currentColor'} />;
      break;
    case 'cooldownClock':
      iconContent = (
        <>
          <circle {...iconPaths.cooldownClock.circle} fill="none" stroke={color || 'currentColor'} strokeWidth="2" />
          <path d={iconPaths.cooldownClock.path} fill="none" stroke={color || 'currentColor'} strokeWidth="2" strokeLinecap="round" />
        </>
      );
      break;
    case 'inCorner':
    case 'row':
    case 'column':
    case 'connectedChain':
      iconContent = (
        <>
          <path d={iconPaths[type].grid} fill="none" stroke={color || 'currentColor'} strokeWidth="1" />
          <path d={iconPaths[type].highlight} fill={color || 'currentColor'} />
        </>
      );
      break;
    case 'presence':
      iconContent = <path d={iconPaths[type]} fill="none" stroke={color || 'currentColor'} strokeWidth="1" />;
      break;
    case 'peakPresence':
      iconContent = (
        <>
          <path d={iconPaths.peakPresence.grid} fill="none" stroke={color || 'currentColor'} strokeWidth="1" />
          <path d={iconPaths.peakPresence.peak} stroke={color || 'currentColor'} strokeWidth="2" />
        </>
      );
      break;
    case 'indicator':
      iconContent = <line {...iconPaths.indicator} stroke={color} strokeWidth="2" />;
      break;
    case 'peakInfluence':
      iconContent = (
        <>
          <path d={iconPaths.peakInfluence.influence} fill={color || 'currentColor'} />
          <path d={iconPaths.peakInfluence.peak} stroke={color || 'currentColor'} strokeWidth="20" />
        </>
      );
      break;
    case 'ruledTiles':
      iconContent = (
        <>
          <g transform="translate(0, 0)">
            <path d={iconPaths.ruledTiles.crown} fill={color || 'currentColor'} />
          </g>
          <g transform="translate(24, 0)">
            <path d={iconPaths.ruledTiles.grid} fill="none" stroke={color || 'currentColor'} strokeWidth="1" />
          </g>
        </>
      );
      break;
    default:
      console.warn(`Unknown icon type: ${type}`);
      return null;
  }

  const svg = (
    <svg {...svgProps}>
      {iconContent}
    </svg>
  );

  return tooltipText ? <Tooltip text={tooltipText}>{svg}</Tooltip> : svg;
};

export default createIcon;