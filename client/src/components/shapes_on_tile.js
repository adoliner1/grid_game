import React from 'react';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';
import '../stylesheets/shapes_on_tile.css';

const ShapesOnTile = ({ slots_for_shapes }) => {

    const renderShape = (shape, color) => {
        switch (shape) {
            case 'circle':
                return <Circle playerColor={color} />;
            case 'square':
                return <Square playerColor={color} />;
            case 'triangle':
                return <Triangle playerColor={color} />;
            default:
                return null;
        }
    };

    return (
        <div className="shapes-on-tile">
            {slots_for_shapes.map((slot, index) => (
                <div key={index} className="slot">
                    {slot ? renderShape(slot.shape, slot.color) : null}
                </div>
            ))}
        </div>
    );
};

export default ShapesOnTile;