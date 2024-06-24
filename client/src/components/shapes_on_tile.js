import React, { useState } from 'react';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';
import '../stylesheets/shapes_on_tile.css';

const ShapesOnTile = ({ slots_for_shapes }) => {
    const [slots, setSlots] = useState(slots_for_shapes);

    const addShape = (shape, color) => {
        const nextEmptyIndex = slots.indexOf(null);
        if (nextEmptyIndex !== -1) {
            const newSlots = [...slots];
            newSlots[nextEmptyIndex] = { shape, color };
            setSlots(newSlots);
        }
    };

    const renderShape = (shape, color) => {
        switch (shape) {
            case 'circle':
                return <Circle color={color} />;
            case 'square':
                return <Square color={color} />;
            case 'triangle':
                return <Triangle color={color} />;
            default:
                return null;
        }
    };

    return (
        <div className="shapes-on-tile">
            {slots.map((slot, index) => (
                <div key={index} className="slot">
                    {slot ? renderShape(slot.shape, slot.color) : null}
                </div>
            ))}
            {/* This button is for testing purpose, you can remove or adjust it as needed */}
            <button onClick={() => addShape('circle', 'red')}>Add Red Circle</button>
        </div>
    );
};

export default ShapesOnTile;
