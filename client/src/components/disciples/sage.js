import React from 'react';
import createIcon from '../icons';

const Sage = ({ playerColor, selectable, onClick, size = 18 }) => {
    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;
    const sageIcon = createIcon({ type: 'sage', color: playerColor, tooltipText: 'Sage', width: size, height: size });

    return (
        <div className={className} onClick={onClick}>
            {sageIcon}
        </div>
    );
};

export default Sage;
