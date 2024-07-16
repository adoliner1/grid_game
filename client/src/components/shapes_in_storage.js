// ShapesInStorage.jsx
import React from 'react';
import '../stylesheets/shapes_in_storage.css';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';

const ConversionArrow = ({ player_color, clients_color, whose_turn_is_it, direction, conversion, onConversionArrowClick, numberOfShapeToConvertFrom }) => {
    const isSelectable = (conversion, numberOfShapeToConvertFrom) => {
        if (player_color !== clients_color || whose_turn_is_it !== clients_color) {
            return false;
        }
        
        switch (conversion) {
            case "circle to square":
                return numberOfShapeToConvertFrom >= 3;
            case "square to triangle":
                return numberOfShapeToConvertFrom >= 3;
            case "square to circle":
                return numberOfShapeToConvertFrom >= 1;
            case "triangle to square":
                return numberOfShapeToConvertFrom >= 1;
            default:
                return false;
        }
    };

    const selectable = isSelectable(conversion, numberOfShapeToConvertFrom);
    const clickHandler = selectable ? () => onConversionArrowClick(conversion, player_color) : undefined;

    return (
        <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            className={selectable ? 'arrow-selectable' : ''}
            onClick={clickHandler}
        >
            <path
                d={direction === 'right'
                    ? "M0,10 L15,10 M10,5 L15,10 L10,15"
                    : "M20,10 L5,10 M10,5 L5,10 L10,15"}
                strokeWidth="2"
                fill="none"
            />
        </svg>
    );
};
 
const ShapesInStorage = ({ player_color, clients_color, shapes, whose_turn_is_it, onShapeClick, selectors, tile_in_use, onConversionArrowClick}) => {
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
            <div className="shapes-with-arrows">
                <div className="arrows-row">
                    <div className="arrow-container">
                        <ConversionArrow whose_turn_is_it = {whose_turn_is_it} player_color={player_color} clients_color={clients_color} direction="right" conversion="circle to square" onConversionArrowClick={onConversionArrowClick} numberOfShapeToConvertFrom= {shapes.number_of_circles}/>
                        <ConversionArrow whose_turn_is_it = {whose_turn_is_it} player_color={player_color} clients_color={clients_color} direction="left" conversion="square to circle" onConversionArrowClick={onConversionArrowClick} numberOfShapeToConvertFrom= {shapes.number_of_squares}/>
                    </div>
                    <div className="arrow-container">
                        <ConversionArrow whose_turn_is_it = {whose_turn_is_it} player_color={player_color} clients_color={clients_color} direction="right" conversion="square to triangle" onConversionArrowClick={onConversionArrowClick} numberOfShapeToConvertFrom= {shapes.number_of_squares}/>
                        <ConversionArrow whose_turn_is_it = {whose_turn_is_it} player_color={player_color} clients_color={clients_color} direction="left" conversion="triangle to square" onConversionArrowClick={onConversionArrowClick} numberOfShapeToConvertFrom= {shapes.number_of_triangles}/>
                    </div>
                </div>
                <div className="shapes-row">
                    {renderShapeContainer(Circle, 'circle', shapes.number_of_circles)}
                    {renderShapeContainer(Square, 'square', shapes.number_of_squares)}
                    {renderShapeContainer(Triangle, 'triangle', shapes.number_of_triangles)}
                </div>
            </div>
        </div>
    );
};

export default ShapesInStorage;