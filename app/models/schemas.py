from pydantic import BaseModel

class PassengerRequest(BaseModel):
    passenger_id: str
    from_level: int
    to_level: int

class LiftState(BaseModel):
    current_level: int
    direction: str  # "up", "down", or "idle"
    passengers: list[str]  # List of passenger IDs
    stops: dict[int, list[str]]  # Levels with passengers to pick up/drop off