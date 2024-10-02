import React from 'react';
import createIcon from '../icons';

const Follower = ({ playerColor, selectable, onClick, size = 18 }) => {
    const className = `${selectable ? 'selectable' : ''}`;
    const followerIcon = createIcon({ type: 'follower', color: playerColor, tooltipText: 'Follower', width: size, height: size });

    return (
        <div className={className} onClick={onClick}>
            {followerIcon}
        </div>
    );
};

export default Follower;