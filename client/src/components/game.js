import React, { useState, useEffect, useRef, useCallback } from 'react'
import '../stylesheets/game.css'
import Tile from './tile'
import ShapesInStorage from './shapes_in_storage'
import GameLog from './game_log'

const Game = () => {
    const [gameState, setGameState] = useState(null)
    const socket = useRef(null)
    const [logs, setLogs] = useState([])
    const clientColor = useRef(null)
    const request = useRef({
        'initial_shape_from_storage_or_usable_tile': null,
        "conversions": []
    })
    const [selectors, setSelectors] = useState(['shape-from-storage', 'shape-owned-by-client-color', 'tile', 'usable-by-all', 'usable-by-ruler'])
    const next_part_of_request_to_fill = useRef('initial_shape_from_storage_or_usable_tile')
    const tileInUse = useRef(null)

    const resetConversions = useCallback(() => {
        request.current.conversions.forEach((conversion) => {
            switch (conversion) {
                case 'circle to square':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes, [clientColor.current]: { ...prevState.shapes[clientColor.current] } }
                        newShapes[clientColor.current].number_of_circles += 3
                        newShapes[clientColor.current].number_of_squares -= 1
                        return { ...prevState, shapes: newShapes }
                    })
                    break
                case 'square to triangle':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes, [clientColor.current]: { ...prevState.shapes[clientColor.current] } }
                        newShapes[clientColor.current].number_of_squares += 3
                        newShapes[clientColor.current].number_of_triangles -= 1
                        return { ...prevState, shapes: newShapes }
                    })
                    break
                case 'square to circle':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes, [clientColor.current]: { ...prevState.shapes[clientColor.current] } }
                        newShapes[clientColor.current].number_of_squares += 1
                        newShapes[clientColor.current].number_of_circles -= 1
                        return { ...prevState, shapes: newShapes }
                    })
                    break
                case 'triangle to square':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes, [clientColor.current]: { ...prevState.shapes[clientColor.current] } }
                        newShapes[clientColor.current].number_of_triangles += 1
                        newShapes[clientColor.current].number_of_squares -= 1
                        return { ...prevState, shapes: newShapes }
                    })
                    break
                default:
                    break
            }
        })
    }, [setGameState]);

    const resetRequestAndAssociatedVariables = useCallback(() => {
        setSelectors(['shape-from-storage', 'shape-owned-by-client-color', 'tile', 'usable-by-all', 'usable-by-ruler'])
        request.current = {
            'initial_shape_from_storage_or_usable_tile': null,
            "conversions": []
        }
        next_part_of_request_to_fill.current = 'initial_shape_from_storage_or_usable_tile'
        tileInUse.current = null  
    }, [setSelectors]);

    const sendRequestIfReadyAndUpdateSelectors = () => {
        next_part_of_request_to_fill.current = findFirstNullValueKey(request.current)
        if (next_part_of_request_to_fill.current === null) {
            sendRequest()
            resetRequestAndAssociatedVariables()
        }

        //request not ready to send, tile in use, update selectors based on the next piece of data it needs
        else if (tileInUse.current !== null) {
            setSelectors(tileInUse.current.data_needed_for_use_with_selectors[next_part_of_request_to_fill.current])
        }

        //we're doing a placement from initial state, we have the shape from storage, to get the slot and tile to place it on
        else if (next_part_of_request_to_fill.current === "tile_and_slot_to_place_on")
        {
            setSelectors(['slot', 'empty-or-weaker-shape'])
        }
      }

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message])
    }

    const addKeysToRequest = (data_needed_for_use_with_selectors) => {
        Object.entries(data_needed_for_use_with_selectors).forEach(([key, requirements]) => {
            if (requirements.includes('slot')) {
                request.current[key] = { 'tile': null, 'slot': null }
            } else {
                request.current[key] = null
            }
        })
    }

    const findFirstNullValueKey = (obj) => {
        for (let key in obj) {
            //skip conversions
            if (key === "conversions") {
                continue
            }
            if (obj.hasOwnProperty(key)) {
                if (obj[key] === null) {
                    return key
                } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    if (Object.values(obj[key]).every(value => value === null)) {
                        return key
                    }
                }
            }
        }
        return null
    }

    const handleShapeInStorageClick = (shapeType, color_of_shape) => {
        //special case for initial state, to select a shape from storage to place on a tile
        if (next_part_of_request_to_fill.current === 'initial_shape_from_storage_or_usable_tile') {
            request.current.action = 'place_shape_on_slot'
            request.current[next_part_of_request_to_fill.current] = shapeType
            request.current.shape_type = shapeType
            request.current.tile_and_slot_to_place_on = {'tile': null, "slot": null}
            sendRequestIfReadyAndUpdateSelectors()
        }

        //general case
        else if (selectors.includes('shape-from-storage')) {
            request[next_part_of_request_to_fill.current] = shapeType
            sendRequestIfReadyAndUpdateSelectors()
        }
    }

    const handleConversionArrowClick = (conversion, player_color) => {
        
        switch (conversion) {
            case "circle to square":
                if (gameState.shapes[player_color].number_of_circles >= 3) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        // Create a new object for shapes and update it
                        const newShapes = {
                            ...prevState.shapes,
                            [player_color]: {
                                ...prevState.shapes[player_color],
                                number_of_circles: prevState.shapes[player_color].number_of_circles - 3,
                                number_of_squares: prevState.shapes[player_color].number_of_squares + 1
                            }
                        }
                        return { ...prevState, shapes: newShapes }
                    })
                    addLog(`${player_color} converted 3 circles to 1 square`)
                }
                break
            case "square to triangle":
                if (gameState.shapes[player_color].number_of_squares >= 3) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes,
                            [player_color]: {
                                ...prevState.shapes[player_color],
                                number_of_squares: prevState.shapes[player_color].number_of_squares - 3,
                                number_of_triangles: prevState.shapes[player_color].number_of_triangles + 1
                            }
                        }
                        return { ...prevState, shapes: newShapes }
                    })
                    addLog(`${player_color} converted 3 squares to 1 triangle`)
                }
                break
            case "square to circle":
                if (gameState.shapes[player_color].number_of_squares >= 1) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes,
                            [player_color]: {
                                ...prevState.shapes[player_color],
                                number_of_squares: prevState.shapes[player_color].number_of_squares - 1,
                                number_of_circles: prevState.shapes[player_color].number_of_circles + 1
                            }
                        }
                        return { ...prevState, shapes: newShapes }
                    })
                    addLog(`${player_color} converted 1 square to 1 circle`)
                }
                break
            case "triangle to square":
                if (gameState.shapes[player_color].number_of_triangles >= 1) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes,
                            [player_color]: {
                                ...prevState.shapes[player_color],
                                number_of_triangles: prevState.shapes[player_color].number_of_triangles - 1,
                                number_of_squares: prevState.shapes[player_color].number_of_squares + 1
                            }
                        }
                        return { ...prevState, shapes: newShapes }
                    })
                    addLog(`${player_color} converted 1 triangle to 1 square`)
                }
                break
            default:
                addLog("Unknown conversion type")
        }
    }

    const handleTileClick = (tileIndex) => {
        //special case for initial state to start using a tile
        if (selectors.includes('tile') && next_part_of_request_to_fill.current === 'initial_shape_from_storage_or_usable_tile') {
            request.current.action = 'use_tile'
            request.current[next_part_of_request_to_fill.current] = tileIndex
            request.current.tile_index_to_use = tileIndex
            tileInUse.current = gameState["tiles"][tileIndex]
            
            if (tileInUse.current.data_needed_for_use_with_selectors !== null) {
            addKeysToRequest(tileInUse.current.data_needed_for_use_with_selectors) }
            sendRequestIfReadyAndUpdateSelectors()
        }

        else if (selectors.includes('tile')) {
            request.current[next_part_of_request_to_fill.current] = tileIndex
            sendRequestIfReadyAndUpdateSelectors()
        }
    }

    const handleSlotClick = (tileIndex, slotIndex) => {
        if (selectors.includes('slot')) {
            request.current[next_part_of_request_to_fill.current].tile = tileIndex
            request.current[next_part_of_request_to_fill.current].slot = slotIndex
            sendRequestIfReadyAndUpdateSelectors()
        }
    }

    const playerPasses = () => {
        if (gameState.whose_turn_is_it !== clientColor.current) {
            addLog("Not your turn") }
        else {
            request.current.action = 'pass'
            sendRequest() }
    }

    const sendRequest = () => {
        socket.current.send(JSON.stringify(request.current))
    }
    
    useEffect(() => {
        //socket.current = new WebSocket(`https://thrush-vital-properly.ngrok-free.app/ws/game/`)
        socket.current = new WebSocket(`http://127.0.0.1:8000/ws/game/`)
        socket.current.onopen = () => {
            console.log("WebSocket connection established")
        }
        socket.current.onmessage = (event) => {
            const data = JSON.parse(event.data)
            switch (data.action) {
                case "error":
                    addLog(`Error: ${data.message}`)
                    break
                case "message":
                    addLog(`${data.message}`)
                    break
                case "initialize":
                    setGameState(data.game_state)
                    clientColor.current = data.player_color 
                    break
                case "update_game_state":
                    setGameState(data.game_state)
                    break
                default:
                    addLog("Unknown action received")
            }
        }

        socket.current.onclose = () => {
            console.log("WebSocket connection closed")
        }

        return () => {
            if (socket.current) {
                socket.current.close()
            }
        }
    }, [])

    //escape reset
    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                resetConversions()
                resetRequestAndAssociatedVariables()
            }
        }
    
        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [resetConversions, resetRequestAndAssociatedVariables]);

    if (!gameState) {
        return <div>Loading...</div>
    }

    return (
        <div className="game-container">
            <div className="players-shapes-directive-and-log-container">
                <div className={clientColor.current === 'red' ? 'red-text' : 'blue-text'}> You are {clientColor.current} </div>
                <div>
                    {gameState.round_bonuses.map((bonus, index) => (<p key={index} className={index === gameState.round ? 'current-round' : ''}> <b>Round {index}: </b> {bonus}</p>))}
                </div>
                <ShapesInStorage   
                    player_color="red"
                    clients_color={clientColor.current}
                    shapes={gameState.shapes.red}
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeInStorageClick}
                    selectors = {selectors}
                    tile_in_use = {request.current.tile_index_to_use}
                    onConversionArrowClick={handleConversionArrowClick}
                    hasPassed={gameState.player_has_passed.red.toString()}
                    points={gameState.points.red}
                />
                <ShapesInStorage 
                    player_color="blue" 
                    clients_color={clientColor.current}
                    shapes={gameState.shapes.blue} 
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeInStorageClick}
                    selectors = {selectors}
                    tile_in_use = {request.current.tile_index_to_use}
                    onConversionArrowClick={handleConversionArrowClick}
                    hasPassed={gameState.player_has_passed.blue.toString()}
                    points={gameState.points.blue}
                />
                <button 
                    onClick={playerPasses} 
                    disabled={gameState.whose_turn_is_it !== clientColor.current}
                    className={gameState.whose_turn_is_it === clientColor.current ? 'btn-enabled' : 'btn-disabled'} >
                    Pass
                </button>
                <GameLog logs={logs} />
            </div>
            <div className="grid">
                {gameState.tiles.map((tile, tile_index) => {
                    return (
                        <Tile
                            key={tile_index}
                            name={tile.name}
                            description={tile.description}
                            shape_to_place={request.current.shape_type}
                            slots_for_shapes={tile.slots_for_shapes}
                            onTileClick={() => handleTileClick(tile_index)}
                            onSlotClick={(slotIndex) => handleSlotClick(tile_index, slotIndex)}
                            selectors={selectors}
                            tile_index = {tile_index}
                            tile_in_use = {request.current.tile_index_to_use}
                            whose_turn_is_it={gameState.whose_turn_is_it}
                            has_use_action_for_all = {gameState["tiles"][tile_index].has_use_action_for_all}
                            has_use_action_for_ruler = {gameState["tiles"][tile_index].has_use_action_for_ruler}
                            ruler = {gameState.tiles[tile_index].ruler}
                            clients_color = {clientColor.current}
                        />
                    )
                })} 
            </div>
        </div>
    )   
}

export default Game