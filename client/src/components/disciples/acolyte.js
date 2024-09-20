import React from 'react';
import createIcon from '../icons';

const Acolyte = ({ playerColor, selectable, onClick, size = 18 }) => {
    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;
    const acolyteIcon = createIcon({ type: 'acolyte', color: playerColor, tooltipText: 'Acolyte', width: size, height: size });

    return (
        <div className={className} onClick={onClick}>
            {acolyteIcon}
        </div>
    );
};

export default Acolyte;
