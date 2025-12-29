import { calculateLiftPosition } from '../utils/liftPosition';
import './Building.css';

export default function Building({ building, label }) {
    if (!building) return <div className="building-placeholder">Loading...</div>;

    const liftA = building.lift_a || {};
    const liftB = building.lift_b || {};
    const maxFloors = building.max_floors ?? 10;

    // Dynamic height calculation
    const floorHeight = Math.max(12, Math.min(40, 500 / (maxFloors + 1)));
    const liftHeight = floorHeight - 4;
    const fontSize = Math.max(8, Math.min(12, floorHeight * 0.4));
    const badgeFontSize = Math.max(6, Math.min(10, floorHeight * 0.35));

    const floors = [];
    for (let i = maxFloors; i >= 0; i--) {
        const stopsA = liftA.stops?.[i] || [];
        const stopsB = liftB.stops?.[i] || [];

        floors.push(
            <div key={i} className="floor" style={{ height: `${floorHeight}px`, fontSize: `${fontSize}px` }}>
                <div className="floor-number">{i}</div>
                <div className="floor-content">
                    {stopsA.map(s => (
                        <span
                            key={s.passenger_id}
                            className={`badge ${s.type === 'pickup' ? 'badge-a' : 'badge-exit'}`}
                            style={{ fontSize: `${badgeFontSize}px`, padding: floorHeight < 20 ? '0 2px' : '2px 5px' }}
                        >
                            {s.passenger_id.replace(/_[AB]$/, '')}
                        </span>
                    ))}
                    {stopsB.map(s => (
                        <span
                            key={s.passenger_id}
                            className={`badge ${s.type === 'pickup' ? 'badge-b' : 'badge-exit'}`}
                            style={{ fontSize: `${badgeFontSize}px`, padding: floorHeight < 20 ? '0 2px' : '2px 5px' }}
                        >
                            {s.passenger_id.replace(/_[AB]$/, '')}
                        </span>
                    ))}
                </div>
            </div>
        );
    }

    // Use utility function for position calculation
    const liftABottom = calculateLiftPosition(liftA.level || 0, floorHeight);
    const liftBBottom = calculateLiftPosition(liftB.level || 0, floorHeight);

    return (
        <div className="building">
            <div className="building-header">
                <span className="building-label">{label}</span>
                <span className="building-algo">{building.algorithm?.toUpperCase() || 'SCAN'}</span>
            </div>
            <div className="building-body">
                <div className="shaft">
                    <div
                        className="lift lift-a"
                        style={{ bottom: `${liftABottom}px`, height: `${liftHeight}px` }}
                    >
                        {liftA.passengers?.length || 0}
                    </div>
                </div>
                <div className="shaft">
                    <div
                        className="lift lift-b"
                        style={{ bottom: `${liftBBottom}px`, height: `${liftHeight}px` }}
                    >
                        {liftB.passengers?.length || 0}
                    </div>
                </div>
                <div className="floors">
                    {floors}
                </div>
            </div>
            <div className="building-stats">
                <div className="stat">
                    <span className="stat-label">Wait</span>
                    <span className="stat-value">{building.stats?.avg_wait?.toFixed(1) || '0.0'}</span>
                </div>
                <div className="stat">
                    <span className="stat-label">Ride</span>
                    <span className="stat-value">{building.stats?.avg_ride?.toFixed(1) || '0.0'}</span>
                </div>
                <div className="stat">
                    <span className="stat-label">Total</span>
                    <span className="stat-value">{building.stats?.avg_total?.toFixed(1) || '0.0'}</span>
                </div>
                <div className="stat">
                    <span className="stat-label">Done</span>
                    <span className="stat-value">{building.stats?.completed || 0}</span>
                </div>
            </div>
        </div>
    );
}
