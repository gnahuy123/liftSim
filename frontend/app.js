const API_URL = 'http://localhost:8000';
let sessionId = null;
let ws = null;
const MAX_FLOORS = 10;
let nextPassengerNum = parseInt(localStorage.getItem('nextPassengerNum') || '1', 10);

function generatePassengerId() {
    const id = 'P' + String(nextPassengerNum).padStart(3, '0');
    nextPassengerNum += 1;
    localStorage.setItem('nextPassengerNum', String(nextPassengerNum));
    return id;
}

function log(message) {
    const logContainer = document.getElementById('logContainer');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const time = new Date().toLocaleTimeString();
    entry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
    logContainer.insertBefore(entry, logContainer.firstChild);

    while (logContainer.children.length > 20) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (connected) {
        status.className = 'connection-status connected';
        status.innerHTML = '✅ Connected to Session: ' + sessionId;
        document.getElementById('addPassengerBtn').disabled = false;
        document.getElementById('addRandomPassengerBtn').disabled = false;
        document.getElementById('moveLiftBtn').disabled = false;
    } else {
        status.className = 'connection-status disconnected';
        status.innerHTML = '⚠️ Not Connected';
        document.getElementById('addPassengerBtn').disabled = true;
        document.getElementById('addRandomPassengerBtn').disabled = true;
        document.getElementById('moveLiftBtn').disabled = true;
    }
}

function renderBuilding() {
    const building = document.getElementById('building');
    building.innerHTML = '';

    // Create container for relative positioning
    const container = document.createElement('div');
    container.className = 'building-container';

    // Create continuous lift shaft
    const liftShaft = document.createElement('div');
    liftShaft.className = 'lift-shaft-container';

    // Create the lift car itself
    const liftCar = document.createElement('div');
    liftCar.id = 'liftCar';
    liftCar.className = 'lift-car';
    liftCar.innerHTML = `
        <span id="passengerCount">0</span> 👤
        <div class="tooltip" id="liftTooltip">No passengers</div>
    `;
    // Initialize at bottom (Level 0)
    liftCar.style.bottom = '5px';
    liftShaft.appendChild(liftCar);

    container.appendChild(liftShaft);

    // Create floors (rendered logic is reversed visually via CSS or order)
    // We want floor 0 at bottom.
    // Let's rely on absolute positioning for the lift, but the floors stacked normally?
    // If I stack floors normally 0 to 10, then 0 is at top? No, HTML default is top-down.
    // So distinct div order: 10 first, then 9, ..., 0 last.

    const floorsContainer = document.createElement('div');
    floorsContainer.id = 'floorsContainer';

    for (let i = MAX_FLOORS; i >= 0; i--) {
        const floor = document.createElement('div');
        floor.className = 'floor';
        floor.id = `floor-${i}`;
        // Fixed height for reliable calculation
        floor.style.height = '70px';

        floor.innerHTML = `
            <div class="floor-number">F${i}</div>
            <div class="exiting-area" id="exiting-${i}"></div>
            <div class="waiting-area" id="waiting-${i}"></div>
        `;

        floorsContainer.appendChild(floor);
    }

    container.appendChild(floorsContainer);
    building.appendChild(container);
}


async function initializeSession() {
    // Reset passenger count for new session
    nextPassengerNum = 1;
    localStorage.setItem('nextPassengerNum', '1');

    try {
        const response = await fetch(`${API_URL}/api/create-session`, {
            method: 'POST'
        });
        const data = await response.json();
        sessionId = data.session_id;

        log(`✅ Session created: ${sessionId}`);
        updateConnectionStatus(true);

        // Render building first so elements exist
        renderBuilding();

        connectWebSocket();
        await updateState();
    } catch (error) {
        log(`❌ Failed to create session: ${error.message}`);
    }
}

function connectWebSocket() {
    ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    ws.onopen = () => {
        log('🔌 WebSocket connected');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        log(`📡 Update: ${data.message || JSON.stringify(data)}`);
        updateState();
    };

    ws.onerror = (error) => {
        log('❌ WebSocket error');
    };

    ws.onclose = () => {
        log('🔌 WebSocket disconnected');
        updateConnectionStatus(false);
    };
}

let autoModeInterval = null;
let autoMoveInterval = null;
let currentSpeed = 1;

function setSpeed(speed) {
    currentSpeed = speed;

    // Update UI buttons
    document.querySelectorAll('.speed-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-speed-${speed}`).classList.add('active');

    // Restart if running
    if (document.getElementById('autoModeToggle').checked) {
        toggleAutoMode(); // Stop
        document.getElementById('autoModeToggle').checked = true; // Keep UI checked
        toggleAutoMode(); // Start
    }
}

async function updateState() {
    if (!sessionId) return;

    try {
        const response = await fetch(`${API_URL}/api/${sessionId}/state`);
        const state = await response.json();

        // Update info panel
        document.getElementById('currentFloor').textContent = state.current_level;
        document.getElementById('direction').textContent = state.direction.toUpperCase();
        document.getElementById('passengers').textContent = state.passengers.length > 0 ? state.passengers.join(', ') : 'None';

        // Update Lift Position
        const liftCar = document.getElementById('liftCar');
        if (liftCar) {
            const floorHeight = 71;
            const bottomPos = (state.current_level * floorHeight) + 5;
            liftCar.style.bottom = `${bottomPos}px`;

            const countSpan = document.getElementById('passengerCount');
            const tooltip = document.getElementById('liftTooltip');

            countSpan.textContent = state.passengers.length;

            if (state.passengers.length > 0) {
                tooltip.textContent = state.passengers.join(', ');
            } else {
                tooltip.textContent = "Empty";
            }
        }

        // Update building visualization (Passenges on floors)
        for (let i = 0; i <= MAX_FLOORS; i++) {
            const waitingDiv = document.getElementById(`waiting-${i}`);
            const exitingDiv = document.getElementById(`exiting-${i}`);

            if (!waitingDiv || !exitingDiv) continue;

            const stops = state.stops[i] || [];

            const pickups = stops.filter(s => s.type === 'pickup');
            const dropoffs = stops.filter(s => s.type === 'dropoff');

            waitingDiv.innerHTML = pickups
                .map(s => `<span class="passenger-badge pickup" title="To: F${s.to_level}">${s.passenger_id} → F${s.to_level}</span>`)
                .join('');

            exitingDiv.innerHTML = dropoffs
                .map(s => `<span class="passenger-badge dropoff" title="Exiting">${s.passenger_id} (Exit)</span>`)
                .join('');
        }

        // Update Passenger Table
        renderPassengerTable(state.active_passengers || [], state);

        // Update Stats from backend
        if (state.stats) {
            document.getElementById('avgWait').textContent = state.stats.avg_wait.toFixed(1);
            document.getElementById('avgRide').textContent = state.stats.avg_ride.toFixed(1);
            document.getElementById('avgTotal').textContent = state.stats.avg_total.toFixed(1);
        }

    } catch (error) {
        log(`❌ Failed to update state: ${error.message}`);
    }
}

function renderPassengerTable(passengers, state) {
    const tbody = document.getElementById('passengerTableBody');
    tbody.innerHTML = '';

    // Sort by ID descending (newest first)
    // Assuming ID format P001, P002... string sort works for same length padding
    const sortedPassengers = [...passengers].sort((a, b) => {
        if (a.passenger_id < b.passenger_id) return 1;
        if (a.passenger_id > b.passenger_id) return -1;
        return 0;
    });

    sortedPassengers.forEach(p => {
        const tr = document.createElement('tr');

        // Badge color based on status
        let statusClass = 'status-waiting';
        if (p.status === 'MOVING') statusClass = 'status-moving';
        if (p.status === 'ARRIVED') statusClass = 'status-arrived';

        // Calculate Intervals
        const currentTick = state.global_tick || 0;
        const created = p.created_at;
        const pickedUp = p.picked_up_at;
        const completed = p.completed_at;

        let waitTime = 0;
        let rideTime = 0;
        let totalTime = 0;

        if (p.status === 'WAITING') {
            waitTime = currentTick - created;
            rideTime = 0;
            totalTime = currentTick - created;
        } else if (p.status === 'MOVING') {
            waitTime = (pickedUp !== null ? pickedUp : currentTick) - created;
            rideTime = currentTick - (pickedUp !== null ? pickedUp : currentTick);
            totalTime = currentTick - created;
        } else if (p.status === 'ARRIVED') {
            waitTime = (pickedUp !== null ? pickedUp : created) - created;
            rideTime = (completed !== null ? completed : currentTick) - (pickedUp !== null ? pickedUp : created);
            totalTime = (completed !== null ? completed : currentTick) - created;
        }

        tr.innerHTML = `
            <td>${p.passenger_id}</td>
            <td>F${p.from_level}</td>
            <td>F${p.to_level}</td>
            <td><span class="status-badge ${statusClass}">${p.status}</span></td>
            <td>${waitTime} ticks</td>
            <td>${rideTime} ticks</td>
            <td>${totalTime} ticks</td>
        `;
        tbody.appendChild(tr);
    });

    // updateStats(passengers); // Removed: Stats are now calculated on backend
}

function updateStats(passengers) {
    // Only verify/count completed passengers for "Averages"? 
    // Or live running averages? User asked "average wait time" etc.
    // Usually Stats are for completed trips. But Wait Time is interesting for Waiting people.
    // Let's calculate based on what makes sense:
    // Avg Wait: All passengers who have entered the lift (or arrived).
    // Avg Ride: All passengers who have arrived.
    // Avg Total: All passengers who have arrived.

    const pickedUpPassengers = passengers.filter(p => p.picked_up_at);
    const arrivedPassengers = passengers.filter(p => p.status === 'ARRIVED');

    let totalWait = 0;
    pickedUpPassengers.forEach(p => {
        totalWait += (p.picked_up_at - p.created_at);
    });
    const avgWait = pickedUpPassengers.length ? (totalWait / pickedUpPassengers.length) : 0;

    let totalRide = 0;
    arrivedPassengers.forEach(p => {
        if (p.picked_up_at && p.completed_at) {
            totalRide += (p.completed_at - p.picked_up_at);
        }
    });
    const avgRide = arrivedPassengers.length ? (totalRide / arrivedPassengers.length) : 0;

    let totalTotal = 0;
    arrivedPassengers.forEach(p => {
        if (p.completed_at && p.created_at) {
            totalTotal += (p.completed_at - p.created_at);
        }
    });
    const avgTotal = arrivedPassengers.length ? (totalTotal / arrivedPassengers.length) : 0;

    document.getElementById('avgWait').textContent = avgWait.toFixed(1);
    document.getElementById('avgRide').textContent = avgRide.toFixed(1);
    document.getElementById('avgTotal').textContent = avgTotal.toFixed(1);
}

function toggleAutoMode() {
    const enabled = document.getElementById('autoModeToggle').checked;

    // Clear existing
    if (autoModeInterval) clearInterval(autoModeInterval);
    if (autoMoveInterval) clearInterval(autoMoveInterval);
    autoModeInterval = null;
    autoMoveInterval = null;

    if (enabled) {
        log(`🤖 Auto Mode STARTED (${currentSpeed}x)`);

        // Base rates:
        // Add Passenger: every 4000ms at 1x? Or 2000ms?
        // User previously had 2000ms default. Let's use 2000ms as Base (1x).
        const passengerRate = 2000 / currentSpeed;

        // Move Lift: every 1000ms at 1x.
        const moveRate = 1000 / currentSpeed;

        // Add passenger loop
        autoModeInterval = setInterval(() => {
            addRandomPassenger();
        }, passengerRate);

        autoMoveInterval = setInterval(() => {
            moveLift();
        }, moveRate);

    } else {
        log('🤖 Auto Mode STOPPED');
    }
}

async function addPassenger() {
    let passengerId = document.getElementById('passengerId').value.trim();
    const fromLevel = parseInt(document.getElementById('fromLevel').value);
    const toLevel = parseInt(document.getElementById('toLevel').value);

    if (isNaN(fromLevel) || isNaN(toLevel)) {
        log('❌ Please fill floor fields');
        return;
    }

    if (fromLevel < 0 || fromLevel > MAX_FLOORS || toLevel < 0 || toLevel > MAX_FLOORS) {
        log(`❌ Floor must be between 0 and ${MAX_FLOORS}`);
        return;
    }

    if (fromLevel === toLevel) {
        log('❌ From and To floors cannot be the same');
        return;
    }

    if (!passengerId) passengerId = generatePassengerId();

    try {
        await fetch(`${API_URL}/api/${sessionId}/add-passenger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ passenger_id: passengerId, from_level: fromLevel, to_level: toLevel })
        });

        log(`✅ Added passenger ${passengerId}: F${fromLevel} → F${toLevel}`);

        // Clear inputs
        document.getElementById('passengerId').value = '';
        document.getElementById('fromLevel').value = '';
        document.getElementById('toLevel').value = '';

        await updateState();
    } catch (error) {
        log(`❌ Failed to add passenger: ${error.message}`);
    }
}

async function addRandomPassenger() {
    const from = Math.floor(Math.random() * (MAX_FLOORS + 1));
    let to = Math.floor(Math.random() * (MAX_FLOORS + 1));
    if (to === from) {
        to = (to + 1) % (MAX_FLOORS + 1);
    }
    const pid = generatePassengerId();

    try {
        await fetch(`${API_URL}/api/${sessionId}/add-passenger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ passenger_id: pid, from_level: from, to_level: to })
        });

        log(`🎲 Random passenger ${pid}: F${from} → F${to}`);
        await updateState();
    } catch (error) {
        log(`❌ Failed to add random passenger: ${error.message}`);
    }
}

async function moveLift() {
    try {
        const response = await fetch(`${API_URL}/api/${sessionId}/move`, { method: 'POST' });
        const data = await response.json();
        log(`🚀 Lift moved: ${JSON.stringify(data)}`);
        await updateState();
    } catch (error) {
        log(`❌ Failed to move lift: ${error.message}`);
    }
}

// Initialize building on load
renderBuilding();

// Expose functions to global scope for inline onclick handlers
window.initializeSession = initializeSession;
window.addPassenger = addPassenger;
window.addRandomPassenger = addRandomPassenger;
window.moveLift = moveLift;
window.toggleAutoMode = toggleAutoMode;
window.setSpeed = setSpeed;
