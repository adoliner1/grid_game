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
  const [leaderboard, setLeaderboard] = useState([]);
  const socket = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch leaderboard data
    fetch('/api/leaderboard')
      .then(response => response.json())
      .then(data => setLeaderboard(data.leaderboard))
      .catch(error => console.error('Error fetching leaderboard:', error));

    fetch('/api/user')
      .then(response => response.json())
      .then(data => {
        if (data.user) {
          setUser(data.user);
        }
      })
      .catch(error => console.error('Error:', error));

    connectWebSocket();
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

  const getRankClass = (elo) => {
    if (elo >= 2000) return 'text-purple-600 font-bold';
    if (elo >= 1800) return 'text-blue-600 font-bold';
    if (elo >= 1600) return 'text-green-600 font-bold';
    if (elo >= 1400) return 'text-yellow-600 font-bold';
    return 'text-gray-600';
  };

  const getRankName = (elo) => {
    if (elo >= 2000) return 'Grandmaster';
    if (elo >= 1800) return 'Master';
    if (elo >= 1600) return 'Expert';
    if (elo >= 1400) return 'Intermediate';
    return 'Beginner';
  };

  return (
    <div className='leaderboard'>
    <h2 className='leader-board-header'>Leaderboard</h2>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Player</th>
          <th>ELO</th>
          <th>W/L</th>
        </tr>
      </thead>
      <tbody>
        {leaderboard.map((player, index) => (
          <tr key={player.username}>
            <td>{index + 1}</td>
            <td>
              <div className="player-info">
                <span className="player-name">{player.username}</span>
                <span className={`player-rank ${getRankClass(player.elo_rating)}`}>
                  {getRankName(player.elo_rating)}
                </span>
              </div>
            </td>
            <td>{player.elo_rating}</td>
            <td>
              <span className="wins">{player.wins}</span>
              /
              <span className="losses">{player.losses}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
  );
}

export default Lobby;