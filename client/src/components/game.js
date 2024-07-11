import React, { useState, useEffect, useRef } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import ShapesInStorage from './shapes_in_storage';
import GameLog from './game_log';

const Game = () => {
    const [gameState, setGameState] = useState(null)
    const socket = useRef(null)
    const [logs, setLogs] = useState([])
    const [clientColor, setClientColor] = useState(null);
    const request = useRef({'initial_shape_from_storage_or_usable_tile': null})
    const [selectors, setSelectors] = useState(['shape-from-storage', 'shape-owned-by-client-color', 'tile', 'usable-by-all', 'usable-by-ruler'])
    const next_part_of_request_to_fill = useRef('initial_shape_from_storage_or_usable_tile')
    const tileInUse = useRef(null)

    const sendRequestIfReadyAndUpdateSelectors = () => {

        //get the next piece of data the request needs by finding a key with a corresponding null value
        next_part_of_request_to_fill.current = findFirstNullValueKey(request.current)

        //request is ready to send because it has no keys with null values, send it, reset selectors and request to default  
        if (next_part_of_request_to_fill.current === null) {
            sendRequest()
            setSelectors(['shape-from-storage', 'shape-owned-by-client-color', 'tile', 'usable-by-all', 'usable-by-ruler'])
            request.current = {'initial_shape_from_storage_or_usable_tile': null}
            next_part_of_request_to_fill.current = 'initial_shape_from_storage_or_usable_tile'
            tileInUse.current = null
            return
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
      };

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message]);
    };

    const addKeysToRequest = (data_needed_for_use_with_selectors) => {
        Object.entries(data_needed_for_use_with_selectors).forEach(([key, requirements]) => {
            if (requirements.includes('slot')) {
                request.current[key] = { 'tile': null, 'slot': null };
            } else {
                request.current[key] = null;
            }
        });
    };

    const findFirstNullValueKey = (obj) => {
        for (let key in obj) {
            if (obj.hasOwnProperty(key)) {
                if (obj[key] === null) {
                    return key;
                } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    if (Object.values(obj[key]).every(value => value === null)) {
                        return key;
                    }
                }
            }
        }
        return null;
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
    };

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
        request.current = {}
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
                setSelectors(['shape-from-storage', 'shape-owned-by-client-color', 'tile', 'usable-by-all', 'usable-by-ruler'])
                request.current = {'initial_shape_from_storage_or_usable_tile': null}
                next_part_of_request_to_fill.current = 'initial_shape_from_storage_or_usable_tile'
                tileInUse.current = null
                addLog("Escape key pressed, selectors and request reset");
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
                <div>
                    <h1>Round Bonuses</h1>
                    {gameState.round_bonuses.map((bonus, index) => (<p key={index}>Round {index + 1}: {bonus}</p>))}
                </div>
                <ShapesInStorage   
                    player_color="red"
                    clients_color={clientColor}
                    shapes={gameState.shapes.red}
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeInStorageClick}
                    selectors = {selectors}
                    tile_in_use = {request.current.tile_index_to_use}
                />
                <ShapesInStorage 
                    player_color="blue" 
                    clients_color={clientColor}
                    shapes={gameState.shapes.blue} 
                    whose_turn_is_it={gameState.whose_turn_is_it}
                    onShapeClick={handleShapeInStorageClick}
                    selectors = {selectors}
                    tile_in_use = {request.current.tile_index_to_use}
                />

                <button 
                    onClick={playerPasses} 
                    disabled={gameState.whose_turn_is_it !== clientColor}
                    className={gameState.whose_turn_is_it === clientColor ? 'btn-enabled' : 'btn-disabled'} >
                Pass
                </button>
                <p> Round: {gameState.round} </p>
                <p> First Player: {gameState.first_player} </p>
                <p> Red Has Passed: {gameState.player_has_passed.red.toString()}</p>
                <p> Blue Has Passed: {gameState.player_has_passed.blue.toString()}</p>
                <p> Red Points: {gameState.points.red}</p>
                <p> Blue Points: {gameState.points.blue}</p>
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
                            clients_color = {clientColor}
                        />
                    );
                })} 
            </div>
        </div>
    );   
};

export default Game;