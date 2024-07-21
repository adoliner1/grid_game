import React, { useState, useEffect, useRef, useCallback } from 'react'
import '../stylesheets/game.css'
import Tile from './tile'
import ShapesInStorage from './shapes_in_storage'
import GameLog from './game_log'

const Game = () => {
    const [gameState, setGameState] = useState(null)
    const [availableActions, setAvailableActions] = useState({}) 
    const [logs, setLogs] = useState([])
    
    const socket = useRef(null)
    const clientColor = useRef(null)
    const request = useRef({'conversions': []})

    const resetConversions = useCallback(() => {
        request.current.conversions.forEach((conversion) => {
            switch (conversion) {
                case 'circle to square':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes_in_storage, [clientColor.current]: { ...prevState.shapes_in_storage[clientColor.current] } }
                        newShapes[clientColor.current].circle += 3
                        newShapes[clientColor.current].square -= 1
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    break
                case 'square to triangle':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes_in_storage, [clientColor.current]: { ...prevState.shapes_in_storage[clientColor.current] } }
                        newShapes[clientColor.current].square += 3
                        newShapes[clientColor.current].triangle -= 1
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    break
                case 'square to circle':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes_in_storage, [clientColor.current]: { ...prevState.shapes_in_storage[clientColor.current] } }
                        newShapes[clientColor.current].square += 1
                        newShapes[clientColor.current].circle -= 1
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    break
                case 'triangle to square':
                    setGameState((prevState) => {
                        const newShapes = { ...prevState.shapes_in_storage, [clientColor.current]: { ...prevState.shapes_in_storage[clientColor.current] } }
                        newShapes[clientColor.current].triangle += 1
                        newShapes[clientColor.current].square -= 1
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    break
                default:
                    break
            }
        })
    }, [setGameState]);

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message])
    }

    const handleShapeInStorageClick = (shape_type) => {
        
        if (availableActions.hasOwnProperty('select_a_shape_in_storage') && availableActions['select_a_shape_in_storage'].includes(shape_type)) {
            request.current.action = 'select_a_shape_in_storage'
            request.current.selected_shape_type_in_storage = shape_type
            sendRequest()
        }
    }

    const handleConversionArrowClick = (conversion, player_color) => {
        
        switch (conversion) {
            case "circle to square":
                if (gameState.shapes_in_storage[player_color].circle >= 3) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes_in_storage,
                            [player_color]: {
                                ...prevState.shapes_in_storage[player_color],
                                circle: prevState.shapes_in_storage[player_color].circle - 3,
                                square: prevState.shapes_in_storage[player_color].square + 1
                            }
                        }
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    addLog(`${player_color} converted 3 circles to 1 square`)
                }
                break
            case "square to triangle":
                if (gameState.shapes_in_storage[player_color].square >= 3) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes_in_storage,
                            [player_color]: {
                                ...prevState.shapes_in_storage[player_color],
                                square: prevState.shapes_in_storage[player_color].square - 3,
                                triangle: prevState.shapes_in_storage[player_color].triangle + 1
                            }
                        }
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    addLog(`${player_color} converted 3 squares to 1 triangle`)
                }
                break
            case "square to circle":
                if (gameState.shapes_in_storage[player_color].square >= 1) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes_in_storage,
                            [player_color]: {
                                ...prevState.shapes_in_storage[player_color],
                                square: prevState.shapes_in_storage[player_color].square - 1,
                                circle: prevState.shapes_in_storage[player_color].circle + 1
                            }
                        }
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    addLog(`${player_color} converted 1 square to 1 circle`)
                }
                break
            case "triangle to square":
                if (gameState.shapes_in_storage[player_color].triangle >= 1) {
                    request.current.conversions.push(conversion)
                    setGameState((prevState) => {
                        const newShapes = {
                            ...prevState.shapes_in_storage,
                            [player_color]: {
                                ...prevState.shapes_in_storage[player_color],
                                triangle: prevState.shapes_in_storage[player_color].triangle - 1,
                                square: prevState.shapes_in_storage[player_color].square + 1
                            }
                        }
                        return { ...prevState, shapes_in_storage: newShapes }
                    })
                    addLog(`${player_color} converted 1 triangle to 1 square`)
                }
                break
            default:
                addLog("Unknown conversion type")
        }
    }

    const handlePassButtonClick = () => {
        request.current.action = "pass"
        sendRequest()
    }
    const handleTileClick = (tile_index) => {
        if (availableActions.hasOwnProperty('select_a_tile')) {
            request.current.action = "select_a_tile"
            request.current.tile_index = tile_index
            sendRequest()
        }
    }

    const handleSlotClick = (tile_index, slot_index) => {
        if (availableActions.hasOwnProperty('select_a_slot')) {
            request.current.action = "select_a_slot"
            request.current.tile_index_of_selected_slot = tile_index
            request.current.index_of_selected_slot = slot_index
            sendRequest()
        }
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
                case "current_available_actions":
                    setAvailableActions(data.available_actions)
                    break
                default:
                    addLog("Unknown action received")
                    break
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

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                resetConversions()
                request.current.action = "reset_current_action"
                sendRequest()
                request.current = {'conversions': []}
            }
        }
    
        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [resetConversions]);

    if (!gameState) {
        return <div>Loading...</div>
    }

    return (
        <div className="game-container">
            <div className="info_section">
                <div className={clientColor.current === 'red' ? 'red-text' : 'blue-text'}> You are {clientColor.current} </div>
                <div>
                    {gameState.round_bonuses.map((bonus, index) => (<p key={index} className={index === gameState.round ? 'current-round' : ''}> <b>Round {index}: </b> {bonus}</p>))}
                </div>
                <ShapesInStorage   
                    player_color="red"
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    has_passed={gameState.player_has_passed.red}
                    clients_color={clientColor.current}
                    shapes={gameState.shapes_in_storage.red}
                    points={gameState.points.red}
                    available_actions={availableActions}
                    onShapeClick={handleShapeInStorageClick}
                    onConversionArrowClick={handleConversionArrowClick}
                />
                <ShapesInStorage 
                    player_color="blue" 
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    has_passed={gameState.player_has_passed.blue}
                    clients_color={clientColor.current}
                    shapes={gameState.shapes_in_storage.blue}
                    points={gameState.points.blue}
                    available_actions={availableActions}
                    onShapeClick={handleShapeInStorageClick}
                    onConversionArrowClick={handleConversionArrowClick}
                />
                <button 
                    onClick={handlePassButtonClick} 
                    disabled={!availableActions.hasOwnProperty('pass')}
                    className={availableActions.hasOwnProperty('pass') ? 'btn-enabled' : 'btn-disabled'} >
                    Pass
                </button>
                <GameLog logs={logs} />
            </div>
            <div className="tiles">
                {gameState.tiles.map((tile, tile_index) => {
                    return (
                        <Tile
                            key={tile_index}
                            name={tile.name}
                            description={tile.description}
                            slots_for_shapes={tile.slots_for_shapes}
                            tile_index = {tile_index}
                            ruler = {gameState.tiles[tile_index].ruler}
                            available_actions={availableActions}
                            onTileClick={() => handleTileClick(tile_index)}
                            onSlotClick={(slotIndex) => handleSlotClick(tile_index, slotIndex)}
                        />
                    )
                })} 
            </div>
        </div>
    )   
}

export default Game