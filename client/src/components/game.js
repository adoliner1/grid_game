import React, { useState, useEffect, useRef } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import PlayerShapes from './player_shapes';
import GameLog from './game_log';

const Game = ({}) => {
    const [gameState, setGameState] = useState(null)
    const socket = useRef(null)
    const request = useRef({})
    const [logs, setLogs] = useState([])
    const [clientColor, setClientColor] = useState(null);
    const [directiveText, setDirectiveText] = useState("Select a shape to place on a tile or select a tile action");
    const UIModes = Object.freeze({
        INITIAL: 'INITIAL',
        SELECT_A_TILE_WITH_AN_EMPTY_SLOT: 'SELECT_A_TILE_WITH_AN_EMPTY_SLOT',
        SELECT_A_SHAPE_FROM_STORAGE: 'SELECT_A_SHAPE_FROM_STORAGE',
        SELECT_A_SHAPE_ON_A_TILE: 'SELECT_A_SHAPE_ON_A_TILE',
        IDLE: 'IDLE'
    })
    const [UI_mode, setUIMode] = useState(UIModes.IDLE)

    useEffect(() => {
        setDirectiveText(UI_mode) 
    }, [UI_mode]);

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message]);
    };

    const handleShapeClick = (shapeType, color_of_shape) => {
        if (gameState.whose_turn_is_it !== clientColor) {
            addLog("Not your turn")
            return
        }

        if (color_of_shape !== clientColor) {
            addLog("Those aren't yours")
            return
        }
        if(UI_mode === UIModes.IDLE) {
            setUIMode(UIModes.SELECT_A_TILE_WITH_AN_EMPTY_SLOT)
            request.current.action = 'place_shape_on_tile'
            request.current.shape_type = shapeType
        }
    }

    const handleTileClick = (tileIndex) => {
        if (UI_mode === 'SELECT_A_TILE_WITH_AN_EMPTY_SLOT') {
            request.current.tile_index = tileIndex 
            sendRequest()
            setUIMode(UIModes.IDLE)
        }
    }

    const playerPasses = () => {
        if (gameState.whose_turn_is_it !== clientColor) {
            addLog("Not your turn") }
        else {
            request.current.action = 'pass'
            sendRequest() }
    }

    const sendRequest = () => {
        const new_request = {
            ...request.current
        };
        socket.current.send(JSON.stringify(new_request));
    }
    
    useEffect(() => {
        socket.current = new WebSocket(`ws://localhost:8000/ws/game/`);
        socket.current.onopen = () => {
            console.log("WebSocket connection established");
        };
        
        socket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.action) {
                case "error":
                    addLog(`Error: ${data.message}`);
                    break;
                case "message":
                    addLog(`${data.message}`);
                    break;
                case "initialize":
                    setGameState(data.game_state);
                    setClientColor(data.player_color);
                    break;
                case "update_game_state":
                    setGameState(data.game_state);
                    break;
                default:
                    addLog("Unknown action received");
            }
        };

        socket.current.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            if (socket.current) {
                socket.current.close();
            }
        };
    }, []);

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                setUIMode(UIModes.IDLE);
                request.current = {};
                addLog("Escape key pressed, UI_mode set to IDLE and currentRequest reset");
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    if (!gameState) {
        return <div>Loading...</div>;
    }

    return (
        <div className="game-container">
            <div className="players-shapes-directive-and-log-container">
                <div> you are {clientColor} </div>
                <PlayerShapes   
                    player="red"
                    clients_color={clientColor}
                    shapes={gameState.shapes.red}
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeClick}
                />
                <PlayerShapes 
                    player="blue" 
                    clients_color={clientColor}
                    shapes={gameState.shapes.blue} 
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeClick}
                />

                <button onClick={playerPasses}>Pass</button>

                <div className="directive-text">
                    <p>{directiveText}</p>
                </div>
                <GameLog logs={logs} />
            </div>
            <div className="grid">
                {gameState.tiles.map((tile, index) => {
                    const isSelectable = UI_mode === 'SELECT_A_TILE_WITH_AN_EMPTY_SLOT' && tile.slots_for_shapes.includes(null);
                    return (
                        <Tile
                            key={index}
                            name={tile.name}
                            description={tile.description}
                            ruling_criteria={tile.ruling_criteria}
                            ruling_benefits={tile.ruling_benefits}
                            slots_for_shapes={tile.slots_for_shapes}
                            className={isSelectable ? 'tile selectable-tile' : 'tile'}
                            onClick={() => handleTileClick(index)}
                        />
                    );
                })} 
            </div>
        </div>
    );   
};

export default Game;
