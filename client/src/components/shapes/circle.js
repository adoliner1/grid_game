import React from 'react';

const Circle = ({ playerColor, selectable, onClick }) => {

    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    return (
        <svg width='24' height='24' viewBox="0 0 24 24" className={ className } onClick={onClick}>
            <circle cx="12" cy="12" r="10" />
        </svg>
    );
};

export default Circle;
