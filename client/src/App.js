import React from 'react';
import Lobby from './components/lobby'
import Game from './components/game';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <Game gameId="1" />
      </header>
    </div>
  );
};

export default App;