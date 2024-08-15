import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Lobby from './components/lobby';
import Game from './components/game';

const App = () => {
  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li>
              <Link to="/">Lobby</Link>
            </li>
            <li>
              <Link to="/game/1">Game</Link>
            </li>
          </ul>
        </nav>

        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route path="/game/:gameId" element={<Game />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;