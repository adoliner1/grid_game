import React from 'react';

const Triangle = ({ playerColor, selectable, onClick }) => {

    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    return (
        <svg width='24' height='24' viewBox="0 0 24 24" className={ className } onClick={onClick}>
            <polygon points="12,2 2,22 22,22" />
        </svg>
    );
};

export default Triangle;
