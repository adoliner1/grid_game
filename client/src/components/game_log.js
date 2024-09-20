import React, { useEffect, useRef } from 'react';
import Follower from './disciples/follower';
import Sage from './disciples/sage';
import Acolyte from './disciples/acolyte';

const GameLog = ({ logs }) => {
    const logContainerRef = useRef(null);

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    const discipleSymbols = {
        'follower': Follower,
        'acolyte': Acolyte,
        'sage': Sage,
    }

    const formatLine = (line, index) => {
        const words = line.split(" ");
        let formatted = words.map((w) => {
            const syms = w.match(/(red|blue)_(follower|acolyte|sage)/);
            if (syms) {
                const [, color, disciple] = syms;
                const Component = discipleSymbols[disciple];
                return <Component playerColor={color} size={12} />;
            } else {
                return w;
            }
        });
        formatted = formatted.flatMap((w) => [w, " "]).slice(0, -1);
        return <p key={index}>{formatted}</p>;
    };

    return (
        <div className="game-log" ref={logContainerRef}>
            {logs.map(formatLine)}
        </div>
    );
};

export default GameLog;