import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Lobby from './components/lobby';
import Game from './components/game';

const App = () => {
  if (process.env.NODE_ENV === 'development') {
    return (
      <div className="App">
        <header className="App-header">
          <Game gameId="1" />
        </header>
      </div>
    )
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route path="/game" element={<Game />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App;