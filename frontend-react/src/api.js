const API_URL = import.meta.env.VITE_API_URL || '';

export async function getConfig() {
    const response = await fetch(`${API_URL}/api/config`);
    return response.json();
}

export async function getAlgorithms() {
    const response = await fetch(`${API_URL}/api/algorithms`);
    return response.json();
}

export async function createSession(algorithm = 'scan', max_floors = 10) {
    const response = await fetch(`${API_URL}/api/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm, max_floors })
    });
    return response.json();
}

export async function createComparisonSession(algo1 = 'scan', algo2 = 'scan', max_floors = 10) {
    const response = await fetch(`${API_URL}/api/create-comparison`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm1: algo1, algorithm2: algo2, max_floors })
    });
    return response.json();
}

export async function getState(sessionId) {
    const response = await fetch(`${API_URL}/api/${sessionId}/state`);
    return response.json();
}

export async function addPassenger(sessionId, passengerId, fromLevel, toLevel) {
    const response = await fetch(`${API_URL}/api/${sessionId}/add-passenger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passenger_id: passengerId, from_level: fromLevel, to_level: toLevel })
    });
    return response.json();
}

export async function moveLift(sessionId) {
    const response = await fetch(`${API_URL}/api/${sessionId}/move`, { method: 'POST' });
    return response.json();
}

export function createWebSocket(sessionId, onMessage, onOpen, onClose, onError) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = API_URL.replace(/^http/, 'ws') || `${protocol}//${window.location.host}`;
    const ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);
    ws.onmessage = (event) => onMessage(JSON.parse(event.data));
    ws.onopen = onOpen;
    ws.onclose = onClose;
    ws.onerror = onError;
    return ws;
}
