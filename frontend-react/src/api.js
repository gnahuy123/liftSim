const API_URL = 'http://localhost:8000';

export async function getAlgorithms() {
    const response = await fetch(`${API_URL}/api/algorithms`);
    return response.json();
}

export async function createSession(algorithm = 'scan') {
    const response = await fetch(`${API_URL}/api/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm })
    });
    return response.json();
}

export async function createComparisonSession(algorithm1 = 'scan', algorithm2 = 'scan') {
    const response = await fetch(`${API_URL}/api/create-comparison`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm1, algorithm2 })
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
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    ws.onmessage = (event) => onMessage(JSON.parse(event.data));
    ws.onopen = onOpen;
    ws.onclose = onClose;
    ws.onerror = onError;
    return ws;
}
