import { useState, useEffect, useRef, useCallback } from 'react';
import { createComparisonSession, getState, getAlgorithms, getConfig, createWebSocket } from './api';

export function useLiftSimulation() {
    const [sessionId, setSessionId] = useState(null);
    const [state, setState] = useState(null);
    const [algorithms, setAlgorithms] = useState([]);
    const [config, setConfig] = useState({ max_floors: 10, min_floor: 0 });
    const [algorithm1, setAlgorithm1] = useState('scan');
    const [algorithm2, setAlgorithm2] = useState('scan');
    const [isConnected, setIsConnected] = useState(false);
    const [logs, setLogs] = useState([]);
    const wsRef = useRef(null);
    const sessionIdRef = useRef(null);

    const addLog = useCallback((message) => {
        const time = new Date().toLocaleTimeString();
        setLogs(prev => [{ time, message }, ...prev.slice(0, 19)]);
    }, []);

    // Fetch config and algorithms on mount
    useEffect(() => {
        getConfig()
            .then(data => setConfig(data))
            .catch(err => console.error('Failed to fetch config:', err));

        getAlgorithms()
            .then(data => setAlgorithms(data.algorithms || []))
            .catch(err => addLog(`Failed to fetch algorithms: ${err.message}`));
    }, [addLog]);

    useEffect(() => {
        sessionIdRef.current = sessionId;
    }, [sessionId]);

    // Auto-connect on mount
    useEffect(() => {
        connect(algorithm1, algorithm2);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const refreshState = useCallback(async (sid) => {
        const targetSid = sid || sessionIdRef.current;
        if (!targetSid) return;

        try {
            const newState = await getState(targetSid);
            setState(newState);
        } catch (error) {
            console.error('Failed to fetch state:', error);
        }
    }, []);

    const connect = useCallback(async (algo1 = 'scan', algo2 = 'scan', max_floors = 10) => {
        try {
            if (wsRef.current) {
                wsRef.current.close();
            }

            const data = await createComparisonSession(algo1, algo2, max_floors);
            setSessionId(data.session_id);
            sessionIdRef.current = data.session_id;
            setAlgorithm1(algo1);
            setAlgorithm2(algo2);
            addLog(`Session created: ${data.session_id}`);

            wsRef.current = createWebSocket(
                data.session_id,
                () => refreshState(data.session_id),
                () => {
                    addLog('Connected');
                    setIsConnected(true);
                },
                () => {
                    addLog('Disconnected');
                    setIsConnected(false);
                },
                () => addLog('WebSocket error')
            );

            refreshState(data.session_id);
        } catch (error) {
            addLog(`Failed to connect: ${error.message}`);
        }
    }, [addLog, refreshState]);

    const reconnect = useCallback((algo1, algo2) => {
        connect(algo1, algo2);
    }, [connect]);

    return {
        sessionId,
        state,
        algorithms,
        config,
        algorithm1,
        algorithm2,
        isConnected,
        logs,
        addLog,
        reconnect,
        refreshState: useCallback(() => refreshState(), [refreshState])
    };
}
