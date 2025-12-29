
from pydantic import BaseModel


class PassengerRequest(BaseModel):
    passenger_id: str
    from_level: int
    to_level: int

class CreateSessionRequest(BaseModel):
    algorithm: str | None = "scan"
    max_floors: int | None = 10

class CreateComparisonRequest(BaseModel):
    algorithm1: str | None = "scan"
    algorithm2: str | None = "scan"
    max_floors: int | None = 10

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

class BuildingState(BaseModel):
    algorithm: str
    lift_a: dict  # Simplified for now, or could use LiftState if we had one
    lift_b: dict
    active_passengers: list[PassengerStatus]
    global_tick: int
    stats: dict
    max_floors: int

class ComparisonState(BaseModel):
    type: str = "comparison"
    building1: BuildingState
    building2: BuildingState
    global_tick: int
