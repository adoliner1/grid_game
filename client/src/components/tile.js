import React from 'react';
import '../stylesheets/tile.css';
import ShapesOnTile from './shapes_on_tile';

const Tile = ({
    name,
    description,
    ruling_criteria,
    ruling_benefits,
    slots_for_shapes,
    onClick,
    className,
}) => {
    return (
        <div className={className} onClick={onClick}>
            <h3>{name}</h3>
            <p>{description}</p>
            <p><strong>Ruling Criteria:</strong> {ruling_criteria}</p>
            <p><strong>Ruling Benefits:</strong> {ruling_benefits}</p>
            <ShapesOnTile slots_for_shapes={slots_for_shapes} />
        </div>
    );
};

export default Tile;