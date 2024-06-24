import React from 'react';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';
import '../stylesheets/tile.css';
import ShapesOnTile from './shapes_on_tile';

const Tile = ({
    name,
    description,
    ruling_criteria,
    ruling_benefits,
    slots_for_shapes,
}) => {
    return (
        <div className="tile">
            <h3>{name}</h3>
            <p>{description}</p>
            <p><strong>Ruling Criteria:</strong> {ruling_criteria}</p>
            <p><strong>Ruling Benefits:</strong> {ruling_benefits}</p>
            <ShapesOnTile slots_for_shapes={slots_for_shapes} />
        </div>
    );
};

export default Tile;