import React from 'react';

const Circle = ({ playerColor, selectable, onClick, size = 18 }) => {
    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    return (
        <svg width={ `${size}` } height={ `${size}` } viewBox={ `0 0 ${size} ${size}` } className={ className } onClick={onClick}>
            <circle cx={ `${ size/2 }` } cy={ `${size/2}` } r={ `${size/2.4}` } />
        </svg>
    );
};

export default Circle;
