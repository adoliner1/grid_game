
/*prod
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Lobby from './components/lobby';
import Game from './components/game';

const App = () => {
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
*/

//dev
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
//
