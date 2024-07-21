const ConversionArrow = ({ player_color, clients_color, whose_turn_is_it, direction, conversion, onConversionArrowClick, numberOfShapeToConvertFrom}) => {
    const isSelectable = (conversion, numberOfShapeToConvertFrom) => {
        if (player_color !== clients_color || whose_turn_is_it !== clients_color) {
            return false
        }
        
        switch (conversion) {
            case "circle to square":
                return numberOfShapeToConvertFrom >= 3
            case "square to triangle":
                return numberOfShapeToConvertFrom >= 3
            case "square to circle":
                return numberOfShapeToConvertFrom >= 1
            case "triangle to square":
                return numberOfShapeToConvertFrom >= 1
            default:
                return false
        }
    }

    const selectable = isSelectable(conversion, numberOfShapeToConvertFrom)
    const clickHandler = selectable ? () => onConversionArrowClick(conversion, player_color) : undefined

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
    )
}

export default ConversionArrow