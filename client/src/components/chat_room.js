import React, { useState, useEffect, useRef } from 'react';

function ChatRoom({ players, messages, onSendMessage, currentPlayer }) {
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {
      onSendMessage(newMessage);
      setNewMessage('');
    }
  };

  return (
    <div className="chat-room">
      <div className="players-list">
        <p className='player-list-header'>Players in Lobby</p>
        <ul>
          {players.map((player) => (
            <li key={player.id}>
              {player.name}
            </li>
          ))}
        </ul>
      </div>
      <div className="chat-area">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className="message">
              <strong>{msg.sender}:</strong> {msg.content}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSendMessage}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default ChatRoom;