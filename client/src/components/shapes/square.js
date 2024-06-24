import React from 'react';

const Square = ({ playerColor, selectable, onClick }) => {

    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    return (
        <svg width='24' height='24' viewBox="0 0 24 24" className={ className } onClick={onClick}>
            <rect x="4" y="4" width="16" height="16" />
        </svg>
    );
};

export default Square;
