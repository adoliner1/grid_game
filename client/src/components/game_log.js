import React, { useEffect, useRef } from 'react';
import createIcon from './icons';

const GameLog = ({ logs }) => {
    const logContainerRef = useRef(null);

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    function parseCustomMarkup(text) {
        const parts = text.split(/(\bpower\b|\binfluence\b|\bpoints?\b|\bfollowers?\b|\bacolytes?\b|\bsages?\b|\bleaders?\b|\bred_\w+\b|\bblue_\w+\b)/gi);
        return parts.map((part, index) => {
            const lowerPart = part.toLowerCase();
            const colorMatch = lowerPart.match(/^(red|blue)_(\w+)$/);
           
            if (colorMatch) {
                const [, color, disciple] = colorMatch;
                return createIcon({
                    type: disciple,
                    color: color,
                    width: 12,
                    height: 12,
                    tooltipText: `${color.charAt(0).toUpperCase() + color.slice(1)} ${disciple.charAt(0).toUpperCase() + disciple.slice(1)}`
                });
            }
            switch(lowerPart) {
                case 'power':
                case 'influence':
                case 'follower':
                case 'followers':
                case 'acolyte':
                case 'acolytes':
                case 'sage':
                case 'sages':
                case 'leader':
                case 'leaders':
                    return createIcon({
                        type: lowerPart.replace(/s$/, ''),
                        tooltipText: lowerPart.charAt(0).toUpperCase() + lowerPart.slice(1).replace(/s$/, ''),
                        width: 14,
                        height: 14,
                        className: `${lowerPart.replace(/s$/, '')}-icon`
                    });
                case 'points':
                    return createIcon({
                        type: 'points',
                        tooltipText: lowerPart.charAt(0).toUpperCase() + lowerPart.slice(1).replace(/s$/, ''),
                        width: 14,
                        height: 14,
                        className: `${lowerPart.replace(/s$/, '')}-icon`
                    });
                default:
                    // Split the part into segments that should be processed together
                    const segments = part.split(/(\*\*.*?\*\*|__.*?__|\[\[.*?\]\]|\(\(.*?\)\)|\+\+.*?\+\+|\s+)/g);
                    return segments.map((segment, segmentIndex) => {
                        if (segment.trim() === '') {
                            // Preserve spaces
                            return <span key={`space-${index}-${segmentIndex}`}>{'\u00A0'.repeat(segment.length)}</span>;
                        } else if (/^(\*\*.*\*\*|__.*__|\[\[.*\]\]|\(\(.*\)\)|\+\+.*\+\+)$/.test(segment)) {
                            // Apply markup for special segments
                            return <span key={`markup-${index}-${segmentIndex}`} dangerouslySetInnerHTML={{
                                __html: segment
                                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                    .replace(/__(.*?)__/g, '<i>$1</i>')
                                    .replace(/\^\^(.*?)\^\^/g, '<span style="color: #ff8700">$1</span>')
                                    .replace(/\[\[(.*?)\]\]/g, '<span style="color: #9f00ff">$1</span>')
                                    .replace(/\(\((.*?)\)\)/g, '<span style="color: #007a9a">$1</span>')
                                    .replace(/\+\+(.*?)\+\+/g, '<span style="color: #019000">$1</span>')
                            }} />;
                        } else {
                            // Apply word-specific replacements
                            return <span key={`text-${index}-${segmentIndex}`} dangerouslySetInnerHTML={{
                                __html: segment.replace(/\b(red|blue)\b/gi, (match) => match.charAt(0).toUpperCase() + match.slice(1).toLowerCase())
                            }} />;
                        }
                    });
            }
        });
    }

    const formatLine = (line, index) => {
        const formatted = parseCustomMarkup(line);
        return (
            <p key={index}>
                {formatted.flat().map((part, partIndex) =>
                    React.isValidElement(part)
                        ? React.cloneElement(part, { key: partIndex })
                        : part
                )}
            </p>
        );
    };

    return (
        <div className="game-log" ref={logContainerRef}>
            {logs.map(formatLine)}
        </div>
    );
};

export default GameLog;