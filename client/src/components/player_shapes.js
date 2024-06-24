import React from 'react';
import '../stylesheets/player_shapes.css';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';

const PlayerShapes = ({ player, shapes, color, make_shapes_selectable, onShapeClick }) => {
    return (
        <div className="player-shapes">
            <h3>{player} Shapes</h3>

            <div className="shape-and-amount-container">
                <Circle 
                    playerColor={color} 
                    selectable={make_shapes_selectable && shapes.number_of_circles > 0}
                    onClick={() => onShapeClick("circle")}
                />
                <p>{shapes.number_of_circles}</p>
            </div>

            <div className="shape-and-amount-container">
                <Square 
                    playerColor={color} 
                    selectable={make_shapes_selectable && shapes.number_of_squares > 0}
                    onClick={() => onShapeClick("square")}
                />
                <p>{shapes.number_of_squares}</p>
            </div>

            <div className="shape-and-amount-container">
                <Triangle 
                    playerColor={color} 
                    selectable={make_shapes_selectable && shapes.number_of_triangles > 0}
                    onClick={() => onShapeClick("triangle")}
                />
                <p>{shapes.number_of_triangles}</p>
            </div>
        </div>
    );
};

export default PlayerShapes;
