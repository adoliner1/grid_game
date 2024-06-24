import React, { useState, useEffect, useRef } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import PlayerShapes from './player_shapes';
import GameLog from './game_log';

const Game = ({game_id}) => {
    const [gameState, setGameState] = useState(null)
    const socket = useRef(null);
    const [logs, setLogs] = useState([]);
    const [playerColor, setPlayerColor] = useState(null);
    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message]);
    };

    const UIModes = Object.freeze({
        INITIAL: 'INITIAL',
        SELECT_A_TILE: 'SELECT_A_TILE',
        SELECT_A_SHAPE_FROM_STORAGE: 'SELECT_A_SHAPE_FROM_STORAGE',
        SELECT_A_SHAPE_ON_A_TILE: 'SELECT_A_SHAPE_ON_A_TILE',
        IDLE: 'IDLE'
    });

    const [UI_mode, setUIMode] = useState(UIModes.INITIAL)

    const toggleTurn = () => {
        setGameState(prevState => ({
            ...prevState,
            whose_turn_is_it: prevState.whose_turn_is_it === 'red' ? 'blue' : 'red'
        }));
        const newTurn = gameState.whose_turn_is_it === 'red' ? 'blue' : 'red';
        setUIMode(UIModes.INITIAL)
        setDirectiveText(UI_mode);
        addLog(`Turn passes to ${newTurn} player`);
    };

    const handleShapeClick = (shapeType) => {
        setUIMode(UIModes.SELECT_A_TILE)
        setDirectiveText(UI_mode);
        addLog(`Player clicked on ${shapeType}`);
    };

    const [directiveText, setDirectiveText] = useState("Select a shape to place on a tile or select a tile action");

    useEffect(() => {
        // Establish WebSocket connection
        socket.current = new WebSocket(`ws://localhost:8000/ws/game/`);

        socket.current.onopen = () => {
            console.log("WebSocket connection established");
        };

        socket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setGameState(data.game_state);
            setPlayerColor(data.player_color);
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

    const handleMakeMove = (move) => {
        socket.current.send(JSON.stringify({ action: 'make_move', move }));
    };

    if (!gameState) {
        return <div>Loading...</div>;
    }


    return (
        <div className="game-container">
            <div className="players-shapes-directive-and-log-container">
                <button onClick={toggleTurn}>Toggle Turn</button>
                <div> you are {playerColor} </div>
                <PlayerShapes 
                    player="Player 1"
                    shapes={gameState.shapes.player1}
                    color="red" 
                    make_shapes_selectable={gameState.whose_turn_is_it === 'red'}
                    onShapeClick={handleShapeClick}
                />
                <PlayerShapes 
                    player="Player 2" 
                    shapes={gameState.shapes.player2} 
                    color="blue" 
                    make_shapes_selectable={gameState.whose_turn_is_it === 'blue'}
                    onShapeClick={handleShapeClick}
                />
                <div className="directive-text">
                    <p>{directiveText}</p>
                </div>
                <GameLog logs={logs} />
            </div>
            <div className="grid">
                {gameState.tiles.map((tile, index) => (
                    <Tile
                        key={index}
                        name={tile.name}
                        description={tile.description}
                        ruling_criteria={tile.ruling_criteria}
                        ruling_benefits={tile.ruling_benefits}
                        slots_for_shapes={tile.slots_for_shapes}
                    />
                ))}
            </div>
        </div>
    );
};

export default Game;
