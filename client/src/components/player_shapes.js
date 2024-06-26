import React from 'react';
import '../stylesheets/player_shapes.css';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';

const PlayerShapes = ({ player, clients_color, shapes, whose_turn_is_it, onShapeClick }) => {
    return (
        <div className="player-shapes">
            <h3>{player}'s shapes in storage</h3>

            <div className="shape-and-amount-container">
                <Circle 
                    playerColor={player} 
                    selectable={whose_turn_is_it === clients_color && clients_color === player && shapes.number_of_circles > 0}
                    onClick={() => onShapeClick("circle", player)}
                />
                <p>{shapes.number_of_circles}</p>
            </div>

            <div className="shape-and-amount-container">
                <Square 
                    playerColor={player} 
                    selectable={whose_turn_is_it === clients_color && clients_color === player && shapes.number_of_squares > 0}
                    onClick={() => onShapeClick("square", player)}
                />
                <p>{shapes.number_of_squares}</p>
            </div>

            <div className="shape-and-amount-container">
                <Triangle 
                    playerColor={player} 
                    selectable={whose_turn_is_it === clients_color && clients_color === player && shapes.number_of_triangles > 0}
                    onClick={() => onShapeClick("triangle", player)}
                />
                <p>{shapes.number_of_triangles}</p>
            </div>
        </div>
    );
};

export default PlayerShapes;
