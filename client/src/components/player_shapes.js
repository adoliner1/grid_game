import React from 'react';
import '../stylesheets/player_shapes.css';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';

const PlayerShapes = ({ player_color, clients_color, shapes, whose_turn_is_it, onShapeClick, selectors, tile_in_use}) => {

    const isSelectable = (shapeType, selectors, number_of_shape) => {
        if (whose_turn_is_it !== clients_color) {return false}
        if (!selectors.includes("shape-from-storage")) {return false}
        if (selectors.includes("shape-owned-by-client-color") && clients_color !== player_color) {return false}
        if (number_of_shape <= 0) {return false}
        return true;
    };

    return (
        <div className="player-shapes">
            <h3>{player_color}'s shapes in storage</h3>

            <div className="shape-and-amount-container">
                <Circle 
                    playerColor={player_color} 
                    selectable={isSelectable('circle', selectors, shapes.number_of_circles)}
                    onClick={() => onShapeClick("circle", player_color)}
                />
                <p>{shapes.number_of_circles}</p>
            </div>

            <div className="shape-and-amount-container">
                <Square 
                    playerColor={player_color} 
                    selectable={isSelectable('square', selectors, shapes.number_of_squares)}
                    onClick={() => onShapeClick("square", player_color)}
                />
                <p>{shapes.number_of_squares}</p>
            </div>

            <div className="shape-and-amount-container">
                <Triangle 
                    playerColor={player_color} 
                    selectable={isSelectable('triangle', selectors, shapes.number_of_triangles)}
                    onClick={() => onShapeClick("triangle", player_color)}
                />
                <p>{shapes.number_of_triangles}</p>
            </div>
        </div>
    );
};

export default PlayerShapes;
