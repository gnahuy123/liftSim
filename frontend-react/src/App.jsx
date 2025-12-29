import { useLiftSimulation } from './useLiftSimulation';
import Building from './components/Building';
import Controls from './components/Controls';
import './App.css';

function App() {
  const {
    sessionId,
    state,
    algorithms,
    algorithm1,
    algorithm2,
    isConnected,
    logs,
    addLog,
    reconnect,
    refreshState
  } = useLiftSimulation();

  const building1 = state?.type === 'comparison' ? state.building1 : state;
  const building2 = state?.type === 'comparison' ? state.building2 : null;

  return (
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
          sessionId={sessionId}
          isConnected={isConnected}
          algorithms={algorithms}
          algorithm1={algorithm1}
          algorithm2={algorithm2}
          onReconnect={reconnect}
          onRefreshState={refreshState}
          addLog={addLog}
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
  );
}

export default App;
