import React from 'react'
import '../stylesheets/shapes_in_storage.css'
import Circle from './shapes/circle'
import Square from './shapes/square'
import Triangle from './shapes/triangle'
import ConversionArrow from './conversion_arrow'

const ShapesInStorage = ({player_color, whose_turn_is_it, has_passed, clients_color, shapes, points, available_actions, onShapeClick, onConversionArrowClick}) => {
    const isSelectable = (shape_type, available_actions) => {
        return (
            available_actions.hasOwnProperty('select_a_shape_in_storage') &&
            available_actions['select_a_shape_in_storage'].includes(shape_type) &&
            clients_color === player_color &&
            shapes[shape_type] > 0
        )
    }

    const renderShapeContainer = (ShapeComponent, shape_type, amount_of_shape, available_actions) => {
        const selectable = isSelectable(shape_type, available_actions)
        const clickHandler = selectable ? () => onShapeClick(shape_type, player_color) : undefined
        return (
            <div className="shape-and-amount-container">
                <ShapeComponent
                    playerColor={player_color}
                    selectable={selectable}
                    onClick={clickHandler}
                />
                <p>{amount_of_shape}</p>
            </div>
        )
    }

    return (
        <div className="player-shapes-and-info" >
                <div className="passed-row">
                    <div> <b>Passed:</b> {has_passed.toString()}</div>
                </div>
                <div className="points-row">
                    <div> <b>Points:</b> {points}</div>
                </div>                 
                <div className="arrows-row">
                    <div className="arrow-container">
                        <ConversionArrow whose_turn_is_it={whose_turn_is_it}
                                         player_color={player_color}
                                         clients_color={clients_color}
                                         direction="right"
                                         conversion="circle to square"
                                         onConversionArrowClick={onConversionArrowClick}
                                         numberOfShapeToConvertFrom={shapes.circle}/>

                        <ConversionArrow whose_turn_is_it={whose_turn_is_it}
                                         player_color={player_color}
                                         clients_color={clients_color}
                                         direction="left"
                                         conversion="square to circle"
                                         onConversionArrowClick={onConversionArrowClick}
                                         numberOfShapeToConvertFrom={shapes.square}/>
                    </div>
                    <div className="arrow-container">
                        <ConversionArrow whose_turn_is_it={whose_turn_is_it}
                                         player_color={player_color}
                                         clients_color={clients_color}
                                         direction="right"
                                         conversion="square to triangle" 
                                         onConversionArrowClick={onConversionArrowClick} 
                                         numberOfShapeToConvertFrom={shapes.square}/>

                        <ConversionArrow whose_turn_is_it = {whose_turn_is_it} 
                                         player_color={player_color} 
                                         clients_color={clients_color} 
                                         direction="left" 
                                         conversion="triangle to square" 
                                         onConversionArrowClick={onConversionArrowClick} 
                                         numberOfShapeToConvertFrom={shapes.triangle}/>
                    </div>
                </div>
                <div className="shapes-row">
                    {renderShapeContainer(Circle, 'circle', shapes.circle, available_actions)}
                    {renderShapeContainer(Square, 'square', shapes.square, available_actions)}
                    {renderShapeContainer(Triangle, 'triangle', shapes.triangle, available_actions)}
                </div>
        </div>
    )
}

export default ShapesInStorage