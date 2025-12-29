import { createContext, useContext } from 'react';

// Simulation context for sharing state across components
export const SimulationContext = createContext(null);

// Hook to use simulation context
export function useSimulation() {
    const context = useContext(SimulationContext);
    if (!context) {
        throw new Error('useSimulation must be used within a SimulationProvider');
    }
    return context;
}
