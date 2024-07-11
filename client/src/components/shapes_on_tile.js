import React from 'react';
import Circle from './shapes/circle';
import Square from './shapes/square';
import Triangle from './shapes/triangle';
import '../stylesheets/shapes_on_tile.css';

const shapeHierarchy = {
    'circle': 1,
    'square': 2,
    'triangle': 3
};

const ShapesOnTile = ({ slots_for_shapes, shape_to_place, onSlotClick, selectors, clients_color, tile_index, tile_in_use, whose_turn_is_it, ruler}) => {

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
    }

    const determineIfDirectlyAdjacent = (index1, index2) => {
        if (index1 < 0 || index1 > 8 || index2 < 0 || index2 > 8) {
            return false;
        }
    
        const row1 = Math.floor(index1 / 3);
        const col1 = index1 % 3;
        const row2 = Math.floor(index2 / 3);
        const col2 = index2 % 3;
    
        if (row1 === row2 && Math.abs(col1 - col2) === 1) {
            return true;
        }
    
        if (col1 === col2 && Math.abs(row1 - row2) === 1) {
            return true;
        }
        return false;
    }

    const isSelectable = (slot, selectors) => {
        if (whose_turn_is_it !== clients_color) {return false}
        if (!selectors.includes('slot')) {return false}
        if (selectors.includes('non-empty') && !slot) {return false}
        if (selectors.includes('empty-or-weaker-shape') && slot && shapeHierarchy[shape_to_place] <= shapeHierarchy[slot.shape]) { return false }
        if (selectors.includes('user-color') && slot && clients_color !== slot.color) {return false}
        if (selectors.includes('calling-tile') && tile_index !== tile_in_use) {return false}
        if (selectors.includes('adjacent-to_calling-tile') && !determineIfDirectlyAdjacent(tile_index, tile_in_use)) {return false}
        return true
    };

    return (
        <div className="shapes-on-tile">
            {slots_for_shapes.map((slot, index) => (
                <div 
                    key={index} 
                    className={`slot ${isSelectable(slot, selectors) ? 'selectable-slot' : ''}`}
                    onClick={() => isSelectable(slot, selectors) && onSlotClick(index)}
                >
                    {slot ? renderShape(slot.shape, slot.color) : null}
                </div>
            ))}
        </div>
    );
};

export default ShapesOnTile;