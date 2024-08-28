import React from 'react';

const Square = ({ playerColor, selectable, onClick, size = 18 }) => {
    const className = `owner-${playerColor} ${selectable ? 'selectable' : ''}`;

    return (
        <svg width={ `${size}` } height={ `${size}` } viewBox={ `0 0 ${size} ${size}` } className={ className } onClick={onClick}>
            <rect x={ `${size/6}` } y={ `${size/6}` } width={ `${2*size/3}` } height={ `${2*size/3}` } />
        </svg>
    );
};

export default Square;
