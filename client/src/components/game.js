import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import GameLog from './game_log';
import PlayerHUD from './player_HUD';
import RoundBonusesTable from './round_bonuses_table';

const Game = () => {
    const [gameState, setGameState] = useState(null);
    const [availableActions, setAvailableActions] = useState({});
    const [currentPieceOfDataToFill, setcurrentPieceOfDataToFill] = useState("");
    const [logs, setLogs] = useState([]);
    const [audioEnabled, setAudioEnabled] = useState(true);

    const oldAvailableActions = useRef({});
    const socket = useRef(null);
    const clientColor = useRef(null);
    const request = useRef({});
    const userHasInteracted = useRef(false);
    const clickSound = useRef(null);
    const yourTurnSound = useRef(null);

    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message]);
    };

    const loadAudio = (audioRef, src) => {
        const audio = new Audio(src);
        audio.addEventListener('error', () => {
            console.warn(`Failed to load audio: ${src}`);
            setAudioEnabled(false);
        });
        audio.addEventListener('canplaythrough', () => {
            audioRef.current = audio;
        });
    };

    const playSound = (soundRef) => {
        if (audioEnabled && soundRef.current) {
            soundRef.current.play().catch(error => {
                console.warn('Audio playback failed', error);
                setAudioEnabled(false);
            });
        }
    };

    useEffect(() => {
        loadAudio(clickSound, '/sounds/click.wav');
        loadAudio(yourTurnSound, '/sounds/your_turn.wav');

        const handleUserInteraction = () => {
            userHasInteracted.current = true;
        };
    
        window.addEventListener('click', handleUserInteraction);
        window.addEventListener('keypress', handleUserInteraction);
    
        return () => {
            window.removeEventListener('click', handleUserInteraction);
            window.removeEventListener('keypress', handleUserInteraction);
            if (clickSound.current) clickSound.current.removeEventListener('error', () => {});
            if (yourTurnSound.current) yourTurnSound.current.removeEventListener('error', () => {});
        };
    }, []);

    const handlePassButtonClick = () => {
        playSound(clickSound);
        request.current.client_action = "pass";
        sendRequest();
    };

    const handleChooseNotToReactClick = () => {
        playSound(clickSound);
        request.current.client_action = "do_not_react";
        sendRequest();
    };

    const handleDiscipleInHUDClick = (disciple_type) => {
        if (availableActions.hasOwnProperty('select_a_disciple_in_the_HUD')) {
            playSound(clickSound);
            request.current.client_action = 'select_a_disciple_in_the_HUD';
            request.current[currentPieceOfDataToFill] = disciple_type;
            sendRequest();
        }
    };

    const handleMoveButtonClick = () => {
        if (availableActions.hasOwnProperty('move')) {
            playSound(clickSound);
            request.current.client_action = 'move';
            sendRequest();
        }
    };

    const handleRecruitButtonClick = () => {
        if (availableActions.hasOwnProperty('recruit')) {
            playSound(clickSound);
            request.current.client_action = 'recruit';
            sendRequest();
        }
    };

    const handleExileButtonClick = () => {
        if (availableActions.hasOwnProperty('exile')) {
            playSound(clickSound);
            request.current.client_action = 'exile';
            sendRequest();
        }
    };

    const handleTileClick = (tile_index) => {
        if (availableActions.hasOwnProperty('select_a_tile')) {
            playSound(clickSound);
            request.current.client_action = "select_a_tile";
            request.current[currentPieceOfDataToFill] = tile_index;
            sendRequest();
        }
    };

    const handleSlotClick = (tile_index, slot_index) => {
        playSound(clickSound);
        if (availableActions.hasOwnProperty('select_a_slot_on_a_tile')) {
            request.current.client_action = "select_a_slot_on_a_tile";
            request.current[currentPieceOfDataToFill] = {
                slot_index: slot_index,
                tile_index: tile_index
            };
            sendRequest();
        }
    };

    const handleInfluenceTierClick = (tile_index, tier_index) => {
        playSound(clickSound);
        if (availableActions.hasOwnProperty('select_a_tier')) {
            request.current.client_action = "select_a_tier";
            request.current[currentPieceOfDataToFill] = {
                tier_index: tier_index,
                tile_index: tile_index
            };
            sendRequest();
        }
    };

    const sendRequest = () => {
        socket.current.send(JSON.stringify(request.current));
        request.current = {};
    };
    
    useEffect(() => {
        const game_id = localStorage.getItem('game_id');
        const player_token = localStorage.getItem('player_token');
    
        if (!game_id || !player_token) {
            console.error('Game ID or player token not found');
            return;
        }

        //PROD
        socket.current = new WebSocket(`https://thrush-vital-properly.ngrok-free.app/ws/game/`);
        //DEV
        //socket.current = new WebSocket(`http://127.0.0.1:8000/ws/game/`)
        
        //*PROD
        socket.current.onopen = () => {
            console.log("WebSocket connection established");
            socket.current.send(JSON.stringify({
                action: "authenticate",
                player_token: player_token,
                game_id: game_id
            }));
        };
        /*/

        /*DEV
        socket.current.onopen = () => {
            console.log("WebSocket connection established");
        };
        //DEV*/
        
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
                    clientColor.current = data.player_color;
                    break;
                case "update_game_state":
                    setGameState(data.game_state);
                    break;
                case "current_available_actions":
                    setAvailableActions(data.available_actions);
                    setcurrentPieceOfDataToFill(data.current_piece_of_data_to_fill_in_current_action);
                    break;
                default:
                    addLog("Unknown action received");
                    break;
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
                request.current.client_action = "reset_current_action";
                sendRequest();
            }
        };
    
        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    useEffect(() => {
        if (userHasInteracted.current && 
            Object.keys(oldAvailableActions.current).length === 0 && 
            Object.keys(availableActions).length !== 0) {
            playSound(yourTurnSound);
        }
        oldAvailableActions.current = availableActions;
    }, [availableActions]);

    if (!gameState) {
        return <div>Loading...</div>;
    }

    return (
        <div className="game-container">
          <div className="info_section">
            <div className={clientColor.current === 'red' ? 'red-text' : 'blue-text'}> You are {clientColor.current} </div>
            <RoundBonusesTable gameState={gameState} />
            <PlayerHUD   
              player_color="red"
              whose_turn_is_it={gameState.whose_turn_is_it}
              has_passed={gameState.player_has_passed.red}
              clients_color={clientColor.current}
              points={gameState.points.red}
              presence={gameState.presence.red}
              power={gameState.power.red}
              peak_influence={gameState.peak_influence.red}
              available_actions={availableActions}
              costs_to_exile={gameState.costs_to_exile.red}
              costs_to_recruit={gameState.costs_to_recruit.red}
              recruiting_range={gameState.recruiting_range.red}
              exiling_range={gameState.exiling_range.red}
              onDiscipleClick={handleDiscipleInHUDClick}
            />
            <PlayerHUD 
              player_color="blue" 
              whose_turn_is_it={gameState.whose_turn_is_it}
              has_passed={gameState.player_has_passed.blue}
              clients_color={clientColor.current}
              points={gameState.points.blue}
              presence={gameState.presence.blue}
              power={gameState.power.blue}
              peak_influence={gameState.peak_influence.blue}
              available_actions={availableActions}
              costs_to_exile={gameState.costs_to_exile.blue}
              costs_to_recruit={gameState.costs_to_recruit.blue}
              recruiting_range={gameState.recruiting_range.blue}
              exiling_range={gameState.exiling_range.blue}
              onDiscipleClick={handleDiscipleInHUDClick}
            />
            <div className="action-buttons">
                <button onClick={handlePassButtonClick} disabled={!availableActions.hasOwnProperty('pass')} className={availableActions.hasOwnProperty('pass') ? 'btn-enabled' : 'btn-disabled'}>
                    Pass
                </button>
                <button onClick={handleChooseNotToReactClick} disabled={!availableActions.hasOwnProperty('do_not_react')} className={availableActions.hasOwnProperty('do_not_react') ? 'btn-enabled' : 'btn-disabled'}>
                    Don't Use Reaction
                </button>
                <button onClick={handleMoveButtonClick} disabled={!availableActions.hasOwnProperty('move')} className={availableActions.hasOwnProperty('move') ? 'btn-enabled' : 'btn-disabled'}>
                    Move Leader
                </button>
                <button onClick={handleRecruitButtonClick} disabled={!availableActions.hasOwnProperty('recruit')} className={availableActions.hasOwnProperty('recruit') ? 'btn-enabled' : 'btn-disabled'}>
                    Recruit
                </button>
                <button onClick={handleExileButtonClick} disabled={!availableActions.hasOwnProperty('exile')} className={availableActions.hasOwnProperty('exile') ? 'btn-enabled' : 'btn-disabled'}>
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
                minimum_influence_to_rule={tile.minimum_influence_to_rule}
                type={tile.type}
                red_influence={tile.influence_per_player.red}
                blue_influence={tile.influence_per_player.blue}
                description={tile.description}
                influence_tiers={tile.influence_tiers}
                slots_for_disciples={tile.slots_for_disciples}
                tile_index={tile_index}
                leaders_here={tile.leaders_here}
                ruler={tile.ruler}
                available_actions={availableActions}
                onTileClick={() => handleTileClick(tile_index)}
                onSlotClick={(slotIndex) => handleSlotClick(tile_index, slotIndex)}
                onInfluenceTierClick={(tier_index) => handleInfluenceTierClick(tile_index, tier_index)}
              />
            ))}
          </div>
        </div>
    );
};

export default Game;