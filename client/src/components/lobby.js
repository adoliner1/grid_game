import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../stylesheets/lobby.css';

function Lobby() {
  const [lobbyTables, setLobbyTables] = useState([]);
  const [newLobbyTableName, setNewLobbyTableName] = useState('');
  const [error, setError] = useState('');
  const socket = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      socket.current = new WebSocket('ws://localhost:8000/ws/lobby/') 
    }
    else
    {
      socket.current = new WebSocket(`wss://grid-game.onrender.com/ws/lobby/`)
    }

    
    socket.current.onopen = () => {
      console.log('WebSocket connection established');
      socket.current.send(JSON.stringify({ action: 'fetch_lobby_tables' }));
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.player_token) {
        localStorage.setItem('player_token', data.player_token);
      } else if (data.lobby_tables) {
        setLobbyTables(data.lobby_tables);
      } else if (data.action === 'start_game') {
        // Store the game ID in localStorage
        localStorage.setItem('game_id', data.game_id);
        // Navigate to the game page
        navigate(`/game`);
      } else if (data.error) {
        setError(data.error);
      }
    };

    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, [navigate]);

  const handleCreateLobbyTable = () => {
    socket.current.send(JSON.stringify({ action: 'create_lobby_table', name: newLobbyTableName }));
    setNewLobbyTableName('');
  };

  const handleJoinLobbyTable = (lobbyTableId) => {
    socket.current.send(JSON.stringify({ action: 'join_lobby_table', lobby_table_id: lobbyTableId }));
  };

  return (
    <div className='lobby-div'>
      <h2>Lobby Tables</h2>
      {error && <p className="error">{error}</p>}
      <input
        type="text"
        placeholder="New Lobby Table Name"
        value={newLobbyTableName}
        onChange={(e) => setNewLobbyTableName(e.target.value)}
      />
      <button onClick={handleCreateLobbyTable}>Create Lobby Table</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Players</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {lobbyTables.map((lobbyTable) => (
            <tr key={lobbyTable.id}>
              <td>{lobbyTable.name}</td>
              <td>{lobbyTable.status}</td>
              <td>{lobbyTable.players.filter(Boolean).length} / 2</td>
              <td>
                {lobbyTable.status !== 'Full' && (
                  <button onClick={() => handleJoinLobbyTable(lobbyTable.id)}>Join</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Lobby;