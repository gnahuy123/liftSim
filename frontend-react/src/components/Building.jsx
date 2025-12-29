import './Building.css';

const MAX_FLOORS = 10;

export default function Building({ building, label }) {
    if (!building) return <div className="building-placeholder">Loading...</div>;

    const liftA = building.lift_a || {};
    const liftB = building.lift_b || {};

    const floors = [];
    for (let i = MAX_FLOORS; i >= 0; i--) {
        const stopsA = liftA.stops?.[i] || [];
        const stopsB = liftB.stops?.[i] || [];

        floors.push(
            <div key={i} className="floor">
                <div className="floor-number">{i}</div>
                <div className="floor-content">
                    {stopsA.map(s => (
                        <span key={s.passenger_id} className={`badge ${s.type === 'pickup' ? 'badge-a' : 'badge-exit'}`}>
                            {s.passenger_id.replace(/_[AB]$/, '')}
                        </span>
                    ))}
                    {stopsB.map(s => (
                        <span key={s.passenger_id} className={`badge ${s.type === 'pickup' ? 'badge-b' : 'badge-exit'}`}>
                            {s.passenger_id.replace(/_[AB]$/, '')}
                        </span>
                    ))}
                </div>
            </div>
        );
    }

    const floorHeight = 36;
    const liftABottom = ((liftA.level || 0) * floorHeight) + 2;
    const liftBBottom = ((liftB.level || 0) * floorHeight) + 2;

    return (
        <div className="building">
            <div className="building-header">
                <span className="building-label">{label}</span>
                <span className="building-algo">{building.algorithm?.toUpperCase() || 'SCAN'}</span>
            </div>
            <div className="building-body">
                <div className="shaft">
                    <div className="lift lift-a" style={{ bottom: `${liftABottom}px` }}>
                        {liftA.passengers?.length || 0}
                    </div>
                </div>
                <div className="shaft">
                    <div className="lift lift-b" style={{ bottom: `${liftBBottom}px` }}>
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
