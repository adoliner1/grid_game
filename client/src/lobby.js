import React, { useState, useEffect, useRef } from 'react';
import './lobby.css';

function Lobby() {
  const [playerName, setPlayerName] = useState('');
  const [newPlayerName, setNewPlayerName] = useState('');
  const [lobbyTables, setLobbyTables] = useState([]);
  const [newLobbyTableName, setNewLobbyTableName] = useState('');
  const socket = useRef(null);

  useEffect(() => {
    socket.current = new WebSocket('ws://localhost:8000/ws/lobby/');

    socket.current.onopen = () => {
      console.log('WebSocket connection established');
      socket.current.send(JSON.stringify({ action: 'fetch_lobby_tables' }));
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.lobby_tables) {
        setLobbyTables(data.lobby_tables);
      }
    };

    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, []);

  const handleSetPlayerName = () => {
    setPlayerName(newPlayerName);
  };

  const handleCreateLobbyTable = () => {
    socket.current.send(JSON.stringify({ action: 'create_lobby_table', name: newLobbyTableName }));
  };

  const handleJoinLobbyTable = (lobbyTableId) => {
    socket.current.send(JSON.stringify({ action: 'join_lobby_table', lobby_table_id: lobbyTableId, player_name: playerName }));
  };

  return (
    <div>
      <span>Current Player: {playerName}</span>
      <input
        type="text"
        value={newPlayerName}
        onChange={(e) => setNewPlayerName(e.target.value)}
      />
      <button onClick={handleSetPlayerName}>Set Player Name</button>

      <h2>Lobby Tables</h2>
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
              <td>{lobbyTable.players.map(player => player.name).join(', ')}</td>
              <td>
                <button onClick={() => handleJoinLobbyTable(lobbyTable.id)}>Join</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Lobby;
