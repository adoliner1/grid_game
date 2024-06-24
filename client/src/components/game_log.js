import React from 'react';

const GameLog = ({ logs }) => {
    return (
        <div className="game-log">
            {logs.map((log, index) => (
                <p key={index}>{log}</p>
            ))}
        </div>
    );
};

export default GameLog;