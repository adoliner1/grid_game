import React from 'react';

const Triangle = ({ playerColor, selectable, onClick, size = 18 }) => {

    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    const points = [size/2, 2, 2, size-2, size-2, size-2];
    return (
        <svg width={ `${size}` } height={ `${size}` } viewBox={ `0 0 ${size} ${size}` } className={ className } onClick={onClick}>
            <polygon points={ points.join(", ") } />
        </svg>
    );
};

export default Triangle;
