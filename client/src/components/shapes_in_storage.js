import React from 'react';
import '../stylesheets/shapes_in_storage.css';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';

const ShapesInStorage = ({ player_color, clients_color, shapes, whose_turn_is_it, onShapeClick, selectors, tile_in_use}) => {
    const isSelectable = (shapeType, selectors, number_of_shape) => {
        if (whose_turn_is_it !== clients_color) return false;
        if (!selectors.includes("shape-from-storage")) return false;
        if (selectors.includes("shape-owned-by-client-color") && clients_color !== player_color) return false;
        if (number_of_shape <= 0) return false;
        return true;
    };

    const renderShapeContainer = (ShapeComponent, shapeType, number) => {
        const selectable = isSelectable(shapeType, selectors, number);
        const clickHandler = selectable ? () => onShapeClick(shapeType, player_color) : undefined;

        return (
            <div className="shape-and-amount-container">
                <ShapeComponent
                    playerColor={player_color}
                    selectable={selectable}
                    onClick={clickHandler}
                />
                <p>{number}</p>
            </div>
        );
    };

    return (
        <div className="player-shapes">
            <h3>{player_color}'s shapes in storage</h3>
            {renderShapeContainer(Circle, 'circle', shapes.number_of_circles)}
            {renderShapeContainer(Square, 'square', shapes.number_of_squares)}
            {renderShapeContainer(Triangle, 'triangle', shapes.number_of_triangles)}
        </div>
    );
};

export default ShapesInStorage;