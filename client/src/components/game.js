import React, { useState, useEffect, useRef, useCallback } from 'react'
import '../stylesheets/game.css'
import Tile from './tile'
import ShapesInStorage from './shapes_in_storage'
import GameLog from './game_log'
import Powerup from './powerup'

const Game = () => {
    const [gameState, setGameState] = useState(null)
    const [availableActions, setAvailableActions] = useState({}) 
    const [currentPieceOfDataToFill, setcurrentPieceOfDataToFill] = useState("") 
    const [logs, setLogs] = useState([])
    
    const oldAvailableActions = useRef({})
    const socket = useRef(null)
    const clientColor = useRef(null)
    const request = useRef({'conversions': []})
    const userHasInteracted = useRef(false)
    const clickSound = useRef(new Audio('/sounds/click.wav'));
    const yourTurnSound = useRef(new Audio('/sounds/your_turn.wav'));

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
            request.current.conversions = []
        })
    }, [setGameState]);

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message])
    }

    //just used so we can play "your turn" sound for now - probably not necessary in future
    useEffect(() => {
        const handleUserInteraction = () => {
            userHasInteracted.current = true;
        };
    
        window.addEventListener('click', handleUserInteraction);
        window.addEventListener('keypress', handleUserInteraction);
    
        return () => {
            window.removeEventListener('click', handleUserInteraction);
            window.removeEventListener('keypress', handleUserInteraction);
        };
    }, []);

    const handleConversionArrowClick = (conversion, player_color) => {
        clickSound.current.play();
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
        clickSound.current.play();
        request.current.client_action = "pass"
        sendRequest()
    }

    const handleChooseNotToReactClick = () => {
        clickSound.current.play();
        request.current.client_action = "do_not_react"
        sendRequest()
    }

    const handleShapeInStorageClick = (shape_type) => {
        if (availableActions.hasOwnProperty('select_a_shape_in_storage')) {
            clickSound.current.play();
            request.current.client_action = 'select_a_shape_in_storage'
            request.current[currentPieceOfDataToFill] = shape_type
            sendRequest()
        }
    }

    const handleTileClick = (tile_index) => {
        if (availableActions.hasOwnProperty('select_a_tile')) {
            clickSound.current.play();
            request.current.client_action = "select_a_tile"
            request.current[currentPieceOfDataToFill] = tile_index
            sendRequest() 
        }
    }

    const handleSlotClick = (tile_index, slot_index) => {
        clickSound.current.play();
        if (availableActions.hasOwnProperty('select_a_slot_on_a_tile')) {
            request.current.client_action = "select_a_slot_on_a_tile"
            request.current[currentPieceOfDataToFill] = {}
            request.current[currentPieceOfDataToFill].slot_index = slot_index
            request.current[currentPieceOfDataToFill].tile_index = tile_index
            sendRequest()
        }
    }

    const handlePowerupClick = (powerup_index) => {
        if (availableActions.hasOwnProperty('select_a_powerup')) {
            clickSound.current.play();
            request.current.client_action = "select_a_powerup"
            request.current[currentPieceOfDataToFill] = powerup_index
            sendRequest() 
        }
    }

    const handlePowerupSlotClick = (powerup_index, slot_index) => {
        clickSound.current.play();
        if (availableActions.hasOwnProperty('select_a_slot_on_a_powerup')) {
            request.current.client_action = "select_a_slot_on_a_powerup"
            request.current[currentPieceOfDataToFill] = {}
            request.current[currentPieceOfDataToFill].slot_index = slot_index
            request.current[currentPieceOfDataToFill].powerup_index = powerup_index
            console.log(request.current)
            sendRequest()
        }
    }
    const sendRequest = () => {
        socket.current.send(JSON.stringify(request.current))
        request.current = {'conversions': []}
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
                    clientColor.current = data.player_color 
                    break
                case "update_game_state":
                    setGameState(data.game_state)
                    break
                case "current_available_actions":
                    setAvailableActions(data.available_actions)
                    setcurrentPieceOfDataToFill(data.current_piece_of_data_to_fill_in_current_action)
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
                request.current.client_action = "reset_current_action"
                sendRequest()
            }
        }
    
        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [resetConversions]);

    useEffect(() => {
        if (userHasInteracted.current && 
            Object.keys(oldAvailableActions.current).length === 0 && 
            Object.keys(availableActions).length !== 0) {
            yourTurnSound.current.play();
        }
        oldAvailableActions.current = availableActions;
        console.log(availableActions)
    }, [availableActions]);

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
                <div>
                    {currentPieceOfDataToFill}
                </div>
                <ShapesInStorage   
                    player_color="red"
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    has_passed={gameState.player_has_passed.red}
                    clients_color={clientColor.current}
                    shapes={gameState.shapes_in_storage.red}
                    points={gameState.points.red}
                    presence={gameState.presence.red}
                    peak_power={gameState.peak_power.red}
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
                    presence={gameState.presence.blue}
                    peak_power={gameState.peak_power.blue}
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
                <button 
                    onClick={handleChooseNotToReactClick} 
                    disabled={!availableActions.hasOwnProperty('do_not_react')}
                    className={availableActions.hasOwnProperty('do_not_react') ? 'btn-enabled' : 'btn-disabled'} >
                    Don't Use Reaction
                </button>
                <GameLog logs={logs} />
            </div>
            <div className="tiles-and-powerups">
                <div className="tiles">
                    {gameState.tiles.map((tile, tile_index) => {
                        return (
                            <Tile
                                key={tile_index}
                                name={tile.name}
                                type={tile.type}
                                red_power={tile.power_per_player.red}
                                blue_power={tile.power_per_player.blue}
                                description={tile.description}
                                is_on_cooldown={tile.is_on_cooldown}
                                slots_for_shapes={tile.slots_for_shapes}
                                tile_index={tile_index}
                                ruler={gameState.tiles[tile_index].ruler}
                                available_actions={availableActions}
                                onTileClick={() => handleTileClick(tile_index)}
                                onSlotClick={(slotIndex) => handleSlotClick(tile_index, slotIndex)}
                            />
                        )
                    })}
                </div>
                <div className="powerups">
                    <div className="red-powerups">
                        {gameState.powerups.red.map((powerup, powerup_index) => {
                            return (
                                <Powerup
                                    key={powerup_index}
                                    clients_color={clientColor.current}
                                    description={powerup.description}
                                    is_on_cooldown={powerup.is_on_cooldown}
                                    powerup_index={powerup_index}
                                    available_actions={availableActions}
                                    onPowerupClick={() => handlePowerupClick(powerup_index)}
                                    slots_for_shapes={powerup.slots_for_shapes}
                                    onPowerupSlotClick={(slotIndex) => handlePowerupSlotClick(powerup_index, slotIndex)}
                                    playerColorOfPowerups={"red"}
                                />
                            )
                        })}
                    </div>
                    <div className="blue-powerups">
                        {gameState.powerups.blue.map((powerup, powerup_index) => {
                            return (
                                <Powerup
                                    key={powerup_index}
                                    clients_color={clientColor.current}
                                    description={powerup.description}
                                    is_on_cooldown={powerup.is_on_cooldown}
                                    powerup_index={powerup_index}
                                    available_actions={availableActions}
                                    onPowerupClick={() => handlePowerupClick(powerup_index)}
                                    slots_for_shapes={powerup.slots_for_shapes}
                                    onPowerupSlotClick={(slotIndex) => handlePowerupSlotClick(powerup_index, slotIndex)}
                                    playerColorOfPowerups={"blue"}
                                />
                            )
                        })}
                    </div>
                </div>
            </div>
        </div>
    )   
}

export default Game