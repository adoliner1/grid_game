import React, { useState, useEffect, useRef } from 'react';
import '../stylesheets/game.css';
import Tile from './tile';
import PlayerShapes from './player_shapes';

const Game = ({game_id}) => {
    const [gameState, setGameState] = useState({
        shapes: {
            player1: { number_of_circles: 5, number_of_squares: 12, number_of_triangles: 0 },
            player2: { number_of_circles: 7, number_of_squares: 0, number_of_triangles: 0 }
        },
        tiles: Array.from({ length: 9 }, (_, index) => ({
            name: `Tile ${index + 1}`,
            description: `This is tile ${index + 1}`,
            ruling_criteria: `Criterion ${index + 1}`,
            ruling_benefits: `Benefit ${index + 1}`,
            slots_for_shapes: Array(Math.floor(Math.random() * 5) + 1).fill(null)
        })),
        whose_turn_is_it: "red"
    })
    const socket = useRef(null);

    const [UI_state, setUIState] = useState({
        current_mode: "idle"
    })

    const toggleTurn = () => {
        setGameState(prevState => ({
            ...prevState,
            whose_turn_is_it: prevState.whose_turn_is_it === 'red' ? 'blue' : 'red'
        }));
    };

    const handleShapeClick = (shapeType) => {
        console.log(`Shape clicked: ${shapeType}`);
        // Handle the shape click, e.g., send to server, update state, etc.
    };

    useEffect(() => {
        // Establish WebSocket connection
        socket.current = new WebSocket(`ws://localhost:8000/ws/game/${game_id}/`);

        socket.current.onopen = () => {
            console.log("WebSocket connection established");
            //socket.current.send(JSON.stringify({ action: 'join_game', player_name: playerName }));
        };

        socket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setGameState(data);
        };

        socket.current.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            if (socket.current) {
                socket.current.close();
            }
        };
    }, [game_id]);

    const handleMakeMove = (move) => {
        socket.current.send(JSON.stringify({ action: 'make_move', move }));
    };

    return (
        <div className="game-container">
            <div className="players-shapes-container">
                <button onClick={toggleTurn}>Toggle Turn</button>
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
