import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from './chat_room';
import '../stylesheets/lobby.css';

function Lobby() {
  const [lobbyTables, setLobbyTables] = useState([]);
  const [error, setError] = useState('');
  const [lobbyPlayers, setLobbyPlayers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [user, setUser] = useState(null);
  const [playerInfo, setPlayerInfo] = useState(null);
  const socket = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/api/user')
      .then(response => response.json())
      .then(data => {
        if (data.user) {
          setUser(data.user);
        }
      })
      .catch(error => console.error('Error:', error));

    connectWebSocket()
  }, []);

  const connectWebSocket = () => {
    if (process.env.NODE_ENV === 'development') {
      socket.current = new WebSocket('ws://localhost:8000/ws/lobby/')
    } else {
      socket.current = new WebSocket(`wss://grid-game.onrender.com/ws/lobby/`)
    }
    
    socket.current.onopen = () => {
      console.log('WebSocket connection established')
      
      // Send identity info
      socket.current.send(JSON.stringify({ 
        action: 'authenticate',
        auth_type: user ? 'google' : 'guest'
      }))
    }

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data)
     
      if (data.error) {
        setError(data.error);
        return;
      }
     
      switch (data.action) {
        case 'update_lobby_players':
          setLobbyPlayers(data.players);
          break;
        case 'update_lobby_tables': 
          setLobbyTables(data.lobby_tables);
          break;
        case 'update_player_info':
          setPlayerInfo(data.player_info);
          localStorage.setItem('player_info', JSON.stringify(data.player_info));
          break;
        case 'start_game':
          localStorage.setItem('game_id', data.game_id);
          navigate(`/game`);
          break;
        case 'update_messages':
          setMessages(prevMessages => [...prevMessages, data.message]);
          break;
      }
     };
  }

  useEffect(() => {
    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, []);

  const handleCreateLobbyTable = () => {
    socket.current.send(JSON.stringify({ 
      action: 'create_lobby_table', 
      name: playerInfo?.player_name || "New Table"
    }));
  };

  const handleJoinLobbyTable = (lobbyTableId) => {
    socket.current.send(JSON.stringify({ action: 'join_lobby_table', lobby_table_id: lobbyTableId }));
  };

  const handleSendMessage = (message) => {
    socket.current.send(JSON.stringify({ action: 'send_message', message }));
  };

  const handleLogin = () => {
    window.location.href = '/login';
  };

  const handleLogout = () => {
    fetch('/logout')
      .then(() => {
        setUser(null);
      })
      .catch(error => console.error('Error:', error));
  };

  return (
    <div className='lobby-container'>
      <div className='top-section'>
        <div className='left-column'>
          <p>
            <a href="https://docs.google.com/document/d/1hKATNg-UF-BnJWOyNphiv7hFPWJ81dy6zJYiH3Jl96I/edit?tab=t.0" target="_blank" rel="noopener noreferrer">Rules</a>
          </p>
          {user ? (
            <>
              {playerInfo && <p>{playerInfo.player_name}</p>}
              <button onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <button onClick={handleLogin}>Login with Google</button>
          )}
        </div>
        <div className='lobby-tables'>
          <table>
            <thead>
              <tr>
                <th>Table</th>
                <th>Players</th>
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
                  <td>
                    {lobbyTable.players.map(player => 
                      <span key={player.id} className={player.is_guest ? 'text-gray-500' : 'text-black'}>
                        {player.name}
                      </span>
                    ).reduce((prev, curr) => [prev, ', ', curr])}
                  </td>
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
        currentPlayer={playerInfo}
      />
    </div>
  );
}

export default Lobby;