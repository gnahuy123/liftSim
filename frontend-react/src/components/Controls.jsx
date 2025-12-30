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
    const [selectedAlgo1, setSelectedAlgo1] = useState(algorithm1);
    const [selectedAlgo2, setSelectedAlgo2] = useState(algorithm2);
    const [numLevels, setNumLevels] = useState(config?.max_floors ?? 10);
    const [spawnRate, setSpawnRate] = useState(0.5); // Passengers per second
    const [realisticMode, setRealisticMode] = useState(true);

    const [autoMode, setAutoMode] = useState(false);
    const [speed, setSpeed] = useState(1);
    const [passengersAdded, setPassengersAdded] = useState(0);

    // Use useRef for passenger counter (React-safe)
    const passengerNumRef = useRef(1);
    const autoModeRef = useRef(null);
    const autoMoveRef = useRef(null);

    // Sync local settings with props when simulation restarts/updates
    useEffect(() => {
        setSelectedAlgo1(algorithm1);
        setSelectedAlgo2(algorithm2);
        setNumLevels(config?.max_floors ?? 10);
    }, [algorithm1, algorithm2, config?.max_floors]);


    const generatePassengerId = () => {
        const id = 'P' + String(passengerNumRef.current).padStart(3, '0');
        passengerNumRef.current += 1;
        return id;
    };

    useEffect(() => {
        if (autoMode && sessionId) {
            const passengerInterval = (1000 / spawnRate) / speed;
            const moveInterval = 1000 / speed;

            autoModeRef.current = setInterval(async () => {
                let from, to;

                if (realisticMode) {
                    // 50% Ground -> Random, 50% Random -> Ground
                    if (Math.random() < 0.5) {
                        from = 0;
                        to = Math.floor(Math.random() * numLevels) + 1;
                    } else {
                        from = Math.floor(Math.random() * numLevels) + 1;
                        to = 0;
                    }
                } else {
                    from = Math.floor(Math.random() * (numLevels + 1));
                    to = Math.floor(Math.random() * (numLevels + 1));
                    if (to === from) to = (to + 1) % (numLevels + 1);
                }

                const pid = generatePassengerId();

                try {
                    await addPassenger(sessionId, pid, from, to);
                    addLog(`Added ${pid}: ${from}→${to}`);
                    setPassengersAdded(prev => prev + 1);
                    onRefreshState();
                } catch (err) {
                    addLog(`Error: ${err.message}`);
                }
            }, passengerInterval);

            autoMoveRef.current = setInterval(async () => {
                try {
                    await moveLift(sessionId);
                    onRefreshState();
                } catch (err) {
                    addLog(`Move error: ${err.message}`);
                }
            }, moveInterval);

            addLog(`Auto mode started (${speed}x)`);
        } else {
            if (autoModeRef.current) clearInterval(autoModeRef.current);
            if (autoMoveRef.current) clearInterval(autoMoveRef.current);
        }

        return () => {
            if (autoModeRef.current) clearInterval(autoModeRef.current);
            if (autoMoveRef.current) clearInterval(autoMoveRef.current);
        };
    }, [autoMode, speed, sessionId, addLog, onRefreshState, numLevels, spawnRate, realisticMode]);

    const handleReconnect = () => {
        setAutoMode(false);
        passengerNumRef.current = 1;
        setPassengersAdded(0);
        onReconnect(selectedAlgo1, selectedAlgo2, numLevels);
    };

    const hasChanges = selectedAlgo1 !== algorithm1 ||
        selectedAlgo2 !== algorithm2 ||
        numLevels !== (config?.max_floors ?? 10);

    return (
        <div className="controls">
            <div className="settings-section">
                <h3>Simulation Settings</h3>
                {/* ... existing controls ... */}

                <div className="control-group">
                    <label>Number of Levels: {numLevels}</label>
                    <input
                        type="range"
                        min="2"
                        max="50"
                        value={numLevels}
                        onChange={e => setNumLevels(parseInt(e.target.value))}
                    />
                </div>

                <div className="control-group">
                    <label>Passenger Rate: {spawnRate}/s</label>
                    <input
                        type="range"
                        min="0.1"
                        max="5.0"
                        step="0.1"
                        value={spawnRate}
                        onChange={e => setSpawnRate(parseFloat(e.target.value))}
                    />
                </div>

                <div className="control-group checkbox-group">
                    <label>
                        <input
                            type="checkbox"
                            checked={realisticMode}
                            onChange={e => setRealisticMode(e.target.checked)}
                        />
                        Realistic Traffic (Ground focused)
                    </label>
                </div>
            </div>

            <hr />

            <div className="control-group">
                <label>Building 1 Algorithm</label>
                <select value={selectedAlgo1} onChange={e => setSelectedAlgo1(e.target.value)}>
                    {algorithms.map(a => (
                        <option key={a.name} value={a.name}>{a.description}</option>
                    ))}
                </select>
            </div>

            <div className="control-group">
                <label>Building 2 Algorithm</label>
                <select value={selectedAlgo2} onChange={e => setSelectedAlgo2(e.target.value)}>
                    {algorithms.map(a => (
                        <option key={a.name} value={a.name}>{a.description}</option>
                    ))}
                </select>
            </div>

            <div className="restart-section">
                {hasChanges && (
                    <div className="settings-changed-warning">
                        Settings changed - click Restart to apply
                    </div>
                )}
                <button
                    className={`btn btn-secondary ${hasChanges ? 'btn-pulse' : ''}`}
                    onClick={handleReconnect}
                    disabled={!isConnected}
                >
                    Restart Simulation
                </button>
            </div>

            <hr />

            <div className="control-group">
                <label>Auto Mode</label>
                <div className="auto-controls">
                    <button
                        className={`btn ${autoMode ? 'btn-active' : 'btn-primary'}`}
                        onClick={() => setAutoMode(!autoMode)}
                        disabled={!isConnected}
                    >
                        {autoMode ? 'Stop Simulation' : 'Start Simulation'}
                    </button>

                    <div className="speed-control">
                        <label>Simulation Speed: {speed}x</label>
                        <div className="speed-buttons">
                            {[0.5, 1, 2, 5, 10].map(s => (
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
                </div>
            </div>

            <div className="stats-row">
                <span>Passengers Added: {passengersAdded}</span>
                <span>Actual Rate: {(spawnRate * speed).toFixed(2)}/s</span>
            </div>
        </div>
    );
}
