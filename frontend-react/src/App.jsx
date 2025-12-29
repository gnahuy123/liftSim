import { useLiftSimulation } from './useLiftSimulation';
import { SimulationContext } from './SimulationContext';
import Building from './components/Building';
import Controls from './components/Controls';
import './App.css';

function App() {
  const simulation = useLiftSimulation();
  const {
    state,
    isConnected,
    logs,
  } = simulation;

  const building1 = state?.type === 'comparison' ? state.building1 : state;
  const building2 = state?.type === 'comparison' ? state.building2 : null;

  return (
    <SimulationContext.Provider value={simulation}>
      <div className="app">
        <header className="header">
          <h1>Lift Simulation Testbed</h1>
          <span className={`status ${isConnected ? 'connected' : ''}`}>
            {isConnected ? 'Connected' : 'Connecting...'}
          </span>
        </header>

        <main className="main">
          <Building building={building1} label="Building 1" />

          <Controls
            sessionId={simulation.sessionId}
            isConnected={simulation.isConnected}
            algorithms={simulation.algorithms}
            config={simulation.config}
            algorithm1={simulation.algorithm1}
            algorithm2={simulation.algorithm2}
            onReconnect={simulation.reconnect}
            onRefreshState={simulation.refreshState}
            addLog={simulation.addLog}
          />

          <Building building={building2} label="Building 2" />
        </main>

        <footer className="log">
          <div className="log-header">Activity Log</div>
          <div className="log-entries">
            {logs.map((entry, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">{entry.time}</span>
                <span className="log-message">{entry.message}</span>
              </div>
            ))}
          </div>
        </footer>
      </div>
    </SimulationContext.Provider>
  );
}

export default App;
