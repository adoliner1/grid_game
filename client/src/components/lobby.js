import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from './chat_room';
import '../stylesheets/lobby.css';

function Lobby() {
  const [lobbyTables, setLobbyTables] = useState([]);
  const [error, setError] = useState('');
  const [lobbyPlayers, setLobbyPlayers] = useState([]);
  const [messages, setMessages] = useState([]);
  const playerToken = useRef(localStorage.getItem('player_token') || null);
  const socket = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      socket.current = new WebSocket('ws://localhost:8000/ws/lobby/')
    } else {
      socket.current = new WebSocket(`wss://grid-game.onrender.com/ws/lobby/`)
    }
   
    socket.current.onopen = () => {
      console.log('WebSocket connection established')
      socket.current.send(JSON.stringify({ action: 'fetch_lobby_tables' }))
      socket.current.send(JSON.stringify({ action: 'fetch_lobby_players' }))
    }
    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.player_token) {
        localStorage.setItem('player_token', data.player_token);
        playerToken.current = data.player_token
      } else if (data.lobby_tables) {
        setLobbyTables(data.lobby_tables);
      } else if (data.action === 'lobby_players') {
        setLobbyPlayers(data.players);
      } else if (data.action === 'update_lobby_players') {
        setLobbyPlayers(data.players);
      } else if (data.action === 'start_game') {
        localStorage.setItem('game_id', data.game_id);
        navigate(`/game`);
      } else if (data.action === 'new_message') {
        setMessages(prevMessages => [...prevMessages, data.message]);
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
    socket.current.send(JSON.stringify({ action: 'create_lobby_table', name: playerToken.current }));
  };

  const handleJoinLobbyTable = (lobbyTableId) => {
    socket.current.send(JSON.stringify({ action: 'join_lobby_table', lobby_table_id: lobbyTableId }));
  };

  const handleSendMessage = (message) => {
    socket.current.send(JSON.stringify({ action: 'send_message', message }));
  };

  return (
    <div className='lobby-container'>
      <div className='top-section'>
        <div className='left-column'>
          <p>
            <a href="https://docs.google.com/document/d/1hKATNg-UF-BnJWOyNphiv7hFPWJ81dy6zJYiH3Jl96I/edit?tab=t.0" target="_blank" rel="noopener noreferrer">Rules</a>
          </p>
        </div>
        <div className='lobby-tables'>
          <table>
            <thead>
              <tr>
                <th>Name</th>
              </tr>
            </thead>
            <tbody>
              {lobbyTables.map((lobbyTable) => (
                <tr 
                  key={lobbyTable.id} 
                  onClick={() => handleJoinLobbyTable(lobbyTable.id)}
                  className="clickable-row"
                >
                  <td>{lobbyTable.name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className='buttons-column'>
          <button className='create-lobby-button' onClick={handleCreateLobbyTable}>Create Table</button>
        </div>
        <div className='leaderboard'>
          <p className='leader-board-header'>Leader Board</p>
        </div>
      </div>
      <ChatRoom
        players={lobbyPlayers}
        messages={messages}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}

export default Lobby;