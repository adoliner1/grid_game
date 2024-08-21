import React, { useEffect, useRef } from 'react';
import Circle from './shapes/circle';
import Triangle from './shapes/triangle';
import Square from './shapes/square';

const GameLog = ({ logs }) => {
    const logContainerRef = useRef(null);

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    const shapeSymbols = {
        'circle': Circle,
        'square': Square,
        'triangle': Triangle,
    }

    const formatLine = (line, index) => {
        const words = line.split(" ");
        let formatted = words.map((w) => {
            const syms = w.match(/(red|blue)_(circle|square|triangle)/);
            if (syms) {
                const [, color, shape] = syms;
                const Component = shapeSymbols[shape];
                return <Component playerColor={ color } size={18} />;
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
