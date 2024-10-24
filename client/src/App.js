import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Lobby from './components/lobby';
import Game from './components/game';
import SetupUsername from './components/setup_username'

const App = () => {
  
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route path="/game" element={<Game />} />
          <Route path="/setup-username" element={<SetupUsername />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App;