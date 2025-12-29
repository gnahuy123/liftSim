import { useState, useEffect, useRef } from 'react';
import { addPassenger, moveLift } from '../api';
import './Controls.css';

export default function Controls({
    sessionId,
    isConnected,
    algorithms,
    config,
    algorithm1,
    algorithm2,
    onReconnect,
    onRefreshState,
    addLog
}) {
    const [fromLevel, setFromLevel] = useState('');
    const [toLevel, setToLevel] = useState('');
    const [selectedAlgo1, setSelectedAlgo1] = useState(algorithm1);
    const [selectedAlgo2, setSelectedAlgo2] = useState(algorithm2);

    const [autoMode, setAutoMode] = useState(false);
    const [speed, setSpeed] = useState(1);
    const [passengersAdded, setPassengersAdded] = useState(0);

    // Use useRef for passenger counter (React-safe)
    const passengerNumRef = useRef(1);
    const autoModeRef = useRef(null);
    const autoMoveRef = useRef(null);

    const maxFloors = config?.max_floors ?? 10;

    const generatePassengerId = () => {
        const id = 'P' + String(passengerNumRef.current).padStart(3, '0');
        passengerNumRef.current += 1;
        return id;
    };

    useEffect(() => {
        if (autoMode && sessionId) {
            const passengerRate = 2000 / speed;
            const moveRate = 1000 / speed;

            autoModeRef.current = setInterval(async () => {
                const from = Math.floor(Math.random() * (maxFloors + 1));
                let to = Math.floor(Math.random() * (maxFloors + 1));
                if (to === from) to = (to + 1) % (maxFloors + 1);
                const pid = generatePassengerId();

                try {
                    await addPassenger(sessionId, pid, from, to);
                    addLog(`Added ${pid}: ${from}→${to}`);
                    setPassengersAdded(prev => prev + 1);
                    onRefreshState();
                } catch (err) {
                    addLog(`Error: ${err.message}`);
                }
            }, passengerRate);

            autoMoveRef.current = setInterval(async () => {
                try {
                    await moveLift(sessionId);
                    onRefreshState();
                } catch (err) {
                    addLog(`Move error: ${err.message}`);
                }
            }, moveRate);

            addLog(`Auto mode started (${speed}x)`);
        } else {
            if (autoModeRef.current) clearInterval(autoModeRef.current);
            if (autoMoveRef.current) clearInterval(autoMoveRef.current);
        }

        return () => {
            if (autoModeRef.current) clearInterval(autoModeRef.current);
            if (autoMoveRef.current) clearInterval(autoMoveRef.current);
        };
    }, [autoMode, speed, sessionId, addLog, onRefreshState, maxFloors]);

    const handleAddPassenger = async () => {
        if (!fromLevel || !toLevel) return;
        const from = parseInt(fromLevel);
        const to = parseInt(toLevel);
        if (from === to || from < 0 || from > maxFloors || to < 0 || to > maxFloors) return;

        const pid = generatePassengerId();
        try {
            await addPassenger(sessionId, pid, from, to);
            addLog(`Added ${pid}: ${from}→${to}`);
            setFromLevel('');
            setToLevel('');
            onRefreshState();
        } catch (err) {
            addLog(`Error: ${err.message}`);
        }
    };

    const handleReconnect = () => {
        setAutoMode(false);
        passengerNumRef.current = 1;
        setPassengersAdded(0);
        onReconnect(selectedAlgo1, selectedAlgo2);
    };

    return (
        <div className="controls">
            <div className="control-group">
                <label>Building 1 Algorithm</label>
                <select value={selectedAlgo1} onChange={e => setSelectedAlgo1(e.target.value)}>
                    {algorithms.map(a => (
                        <option key={a.name} value={a.name}>{a.name.toUpperCase()}</option>
                    ))}
                </select>
            </div>

            <div className="control-group">
                <label>Building 2 Algorithm</label>
                <select value={selectedAlgo2} onChange={e => setSelectedAlgo2(e.target.value)}>
                    {algorithms.map(a => (
                        <option key={a.name} value={a.name}>{a.name.toUpperCase()}</option>
                    ))}
                </select>
            </div>

            <button className="btn btn-secondary" onClick={handleReconnect} disabled={!isConnected}>
                Reset Simulation
            </button>

            <hr />

            <div className="control-group">
                <label>Add Passenger</label>
                <div className="input-row">
                    <input
                        type="number"
                        placeholder="From"
                        min="0"
                        max={maxFloors}
                        value={fromLevel}
                        onChange={e => setFromLevel(e.target.value)}
                    />
                    <span>→</span>
                    <input
                        type="number"
                        placeholder="To"
                        min="0"
                        max={maxFloors}
                        value={toLevel}
                        onChange={e => setToLevel(e.target.value)}
                    />
                    <button className="btn" onClick={handleAddPassenger} disabled={!isConnected}>Add</button>
                </div>
            </div>

            <hr />

            <div className="control-group">
                <label>Auto Mode</label>
                <button
                    className={`btn ${autoMode ? 'btn-active' : 'btn-primary'}`}
                    onClick={() => setAutoMode(!autoMode)}
                    disabled={!isConnected}
                >
                    {autoMode ? 'Stop' : 'Start'}
                </button>
            </div>

            <div className="control-group">
                <label>Speed</label>
                <div className="speed-buttons">
                    {[0.5, 1, 2, 4].map(s => (
                        <button
                            key={s}
                            className={`btn-speed ${speed === s ? 'active' : ''}`}
                            onClick={() => setSpeed(s)}
                        >
                            {s}x
                        </button>
                    ))}
                </div>
            </div>

            <div className="stats-row">
                <span>Passengers: {passengersAdded}</span>
                <span>Rate: ~{(speed * 0.5).toFixed(1)}/s</span>
            </div>
        </div>
    );
}
