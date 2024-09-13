import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import GameLog from './game_log';
import PlayerHUD from './player_HUD';

const Game = () => {
    const [gameState, setGameState] = useState(null)
    const [availableActions, setAvailableActions] = useState({}) 
    const [currentPieceOfDataToFill, setcurrentPieceOfDataToFill] = useState("") 
    const [logs, setLogs] = useState([])

    const oldAvailableActions = useRef({})
    const socket = useRef(null)
    const clientColor = useRef(null)
    const request = useRef({})
    const userHasInteracted = useRef(false)
    const clickSound = useRef(new Audio('/sounds/click.wav'));
    const yourTurnSound = useRef(new Audio('/sounds/your_turn.wav'));

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

    const handleShapeInHUDClick = (shape_type) => {
        if (availableActions.hasOwnProperty('select_a_shape_in_the_HUD')) {
            clickSound.current.play();
            request.current.client_action = 'select_a_shape_in_the_HUD'
            request.current[currentPieceOfDataToFill] = shape_type
            sendRequest()
        }
    }

    const handleMoveButtonClick = () => {
        if (availableActions.hasOwnProperty('move')) {
            clickSound.current.play();
            request.current.client_action = 'move'
            sendRequest()
        }
    }

    const handleRecruitButtonClick = () => {
        if (availableActions.hasOwnProperty('recruit')) {
            clickSound.current.play();
            request.current.client_action = 'recruit'
            sendRequest()
        }
    }

    const handleExileButtonClick = () => {
        if (availableActions.hasOwnProperty('exile')) {
            clickSound.current.play();
            request.current.client_action = 'exile'
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
        if (availableActions.hasOwnProperty('select_a_slot')) {
            request.current.client_action = "select_a_slot"
            request.current[currentPieceOfDataToFill] = {}
            request.current[currentPieceOfDataToFill].slot_index = slot_index
            request.current[currentPieceOfDataToFill].tile_index = tile_index
            sendRequest()
        }
    }

    const handlePowerTierClick = (tile_index, tier_index) => {
        clickSound.current.play();
        if (availableActions.hasOwnProperty('select_a_tier')) {
            request.current.client_action = "select_a_tier"
            request.current[currentPieceOfDataToFill] = {}
            request.current[currentPieceOfDataToFill].tier_index = tier_index
            request.current[currentPieceOfDataToFill].tile_index = tile_index
            sendRequest()
        }
    }

    const sendRequest = () => {
        socket.current.send(JSON.stringify(request.current))
        request.current = {}
    }
    
    useEffect(() => {

        /* PROD
        const game_id = localStorage.getItem('game_id');
        const player_token = localStorage.getItem('player_token');
    
        if (!game_id || !player_token) {
            console.error('Game ID or player token not found');
            return;
        }
            */

        //socket.current = new WebSocket(`https://thrush-vital-properly.ngrok-free.app/ws/game/`)
        socket.current = new WebSocket(`http://127.0.0.1:8000/ws/game/`)
        socket.current.onopen = () => {
            console.log("WebSocket connection established"); }
            // Send the player token for authentication - PROD

            /*
            socket.current.send(JSON.stringify({
                action: "authenticate",
                player_token: player_token,
                game_id: game_id
            }));
        };*/ 

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
                request.current.client_action = "reset_current_action"
                sendRequest()
            }
        }
    
        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, []);

    useEffect(() => {
        if (userHasInteracted.current && 
            Object.keys(oldAvailableActions.current).length === 0 && 
            Object.keys(availableActions).length !== 0) {
            yourTurnSound.current.play();
        }
        oldAvailableActions.current = availableActions;
    }, [availableActions]);

    if (!gameState) {
        return <div>Loading...</div>
    }

    return (
        <div className="game-container">
          <div className="info_section">
            <div className={clientColor.current === 'red' ? 'red-text' : 'blue-text'}> You are {clientColor.current} </div>
            <div>
              {gameState.round_bonuses.map((bonus, index) => (
                <p key={index} className={index === gameState.round ? 'current-round' : ''}>
                  <b>Round {index+1}: </b> {bonus}
                </p>
              ))}
            </div>
            <PlayerHUD   
              player_color="red"
              whose_turn_is_it={gameState.whose_turn_is_it}
              has_passed={gameState.player_has_passed.red}
              clients_color={clientColor.current}
              points={gameState.points.red}
              presence={gameState.presence.red}
              stamina={gameState.stamina.red}
              peak_power={gameState.peak_power.red}
              available_actions={availableActions}
              costs_to_exile={gameState.costs_to_exile.red}
              costs_to_recruit={gameState.costs_to_recruit.red}
              onShapeClick={handleShapeInHUDClick}
            />
            <PlayerHUD 
              player_color="blue" 
              whose_turn_is_it={gameState.whose_turn_is_it}
              has_passed={gameState.player_has_passed.blue}
              clients_color={clientColor.current}
              points={gameState.points.blue}
              presence={gameState.presence.blue}
              stamina={gameState.stamina.blue}
              peak_power={gameState.peak_power.blue}
              available_actions={availableActions}
              costs_to_exile={gameState.costs_to_exile.blue}
              costs_to_recruit={gameState.costs_to_recruit.blue}
              onShapeClick={handleShapeInHUDClick}
            />
            <div className="action-buttons">
                <button onClick={handlePassButtonClick} disabled={!availableActions.hasOwnProperty('pass')} className={availableActions.hasOwnProperty('pass') ? 'btn-enabled' : 'btn-disabled'} >
                    Pass
                </button>
                <button onClick={handleChooseNotToReactClick} disabled={!availableActions.hasOwnProperty('do_not_react')} className={availableActions.hasOwnProperty('do_not_react') ? 'btn-enabled' : 'btn-disabled'} >
                    Don't Use Reaction
                </button>
                <button onClick={handleMoveButtonClick} disabled={!availableActions.hasOwnProperty('move')}className={availableActions.hasOwnProperty('move') ? 'btn-enabled' : 'btn-disabled'} >
                    Move
                </button>
                <button onClick={handleRecruitButtonClick} disabled={!availableActions.hasOwnProperty('recruit')}className={availableActions.hasOwnProperty('recruit') ? 'btn-enabled' : 'btn-disabled'} >
                    Recruit
                </button>
                <button onClick={handleExileButtonClick} disabled={!availableActions.hasOwnProperty('exile')}className={availableActions.hasOwnProperty('exile') ? 'btn-enabled' : 'btn-disabled'} >
                    Exile
                </button>                                     
            </div>
            <GameLog logs={logs} />
          </div>
          <div className="tiles">
            {gameState.tiles.map((tile, tile_index) => (
              <Tile
                key={tile_index}
                name={tile.name}
                minimum_power_to_rule={tile.minimum_power_to_rule}
                type={tile.type}
                red_power={tile.power_per_player.red}
                blue_power={tile.power_per_player.blue}
                description={tile.description}
                power_tiers={tile.power_tiers}
                slots_for_shapes={tile.slots_for_shapes}
                tile_index={tile_index}
                location_of_leaders = {gameState.location_of_leaders}
                ruler={tile.ruler}
                available_actions={availableActions}
                onTileClick={() => handleTileClick(tile_index)}
                onSlotClick={(slotIndex) => handleSlotClick(tile_index, slotIndex)}
                onPowerTierClick={(tier_index) => handlePowerTierClick(tile_index, tier_index)}
              />
            ))}
          </div>
        </div>
      );
    };
    
    export default Game;