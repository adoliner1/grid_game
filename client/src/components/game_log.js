
/** 
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

*/

import React, { useEffect, useRef } from 'react';

const GameLog = ({ logs }) => {
    const logContainerRef = useRef(null);

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="game-log" ref={logContainerRef}>
            {logs.map((log, index) => (
                <p key={index}>{log}</p>
            ))}
        </div>
    );
};

export default GameLog;
