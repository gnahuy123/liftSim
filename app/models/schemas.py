
from pydantic import BaseModel


class PassengerRequest(BaseModel):
    passenger_id: str
    from_level: int
    to_level: int

class CreateSessionRequest(BaseModel):
    algorithm: str | None = "scan"

class CreateComparisonRequest(BaseModel):
    algorithm1: str | None = "scan"
    algorithm2: str | None = "scan"

class StopInfo(BaseModel):
    passenger_id: str
    type: str  # "pickup" or "dropoff"
    to_level: int | None = None

class PassengerStatus(BaseModel):
    passenger_id: str
    from_level: int
    to_level: int
    status: str  # "WAITING", "MOVING", "ARRIVED"
    created_at: float
    picked_up_at: float | None = None
    completed_at: float | None = None

class LiftStats(BaseModel):
    avg_wait: float
    avg_ride: float
    avg_total: float

class LiftState(BaseModel):
    current_level: int
    direction: str  # "up", "down", or "idle"
    passengers: list[str]  # List of passenger IDs inside
    stops: dict[int, list[StopInfo]]  # Levels with passengers to pick up/drop off
    active_passengers: list[PassengerStatus]
    global_tick: int
    stats: LiftStats
    algorithm: str | None = None  # For comparison view

class ComparisonState(BaseModel):
    lift1: LiftState
    lift2: LiftState
    global_tick: int
