import './DesktopMessage.css';

export default function DesktopMessage() {
    return (
        <div className="desktop-message-overlay">
            <div className="desktop-message-content">
                <div className="desktop-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                        <line x1="8" y1="21" x2="16" y2="21"></line>
                        <line x1="12" y1="17" x2="12" y2="21"></line>
                    </svg>
                </div>
                <h1>Desktop Experience Required</h1>
                <p>
                    The Lift Simulation Testbed is designed for a complex multi-building comparison experience
                    that requires a larger screen.
                </p>
                <div className="desktop-suggestion">
                    Please switch to a desktop or laptop device to view the simulation.
                </div>
            </div>
        </div>
    );
}
