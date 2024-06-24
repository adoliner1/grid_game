import React from 'react';
import Lobby from './components/lobby'
import Game from './components/game';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <Game gameId="example_game_id" />
      </header>
    </div>
  );
};

export default App;
