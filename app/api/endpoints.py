"""
API endpoints for lift simulation.
"""
from fastapi import APIRouter, HTTPException

from app.core.algorithms import get_available_algorithms
from app.core.config import DEFAULT_ALGORITHM, MAX_FLOORS, MIN_FLOOR
from app.core.sessions import session_manager
from app.models.schemas import CreateComparisonRequest, CreateSessionRequest, PassengerRequest

router = APIRouter()


@router.get("/config")
async def get_config() -> dict:
    """Get simulation configuration."""
    return {
        "max_floors": MAX_FLOORS,
        "min_floor": MIN_FLOOR,
        "default_algorithm": DEFAULT_ALGORITHM,
    }


@router.get("/algorithms")
async def list_algorithms() -> dict:
    """Returns list of available lift algorithms."""
    return {"algorithms": get_available_algorithms()}


@router.post("/create-session")
async def create_session(request: CreateSessionRequest | None = None) -> dict:
    """Create a single-building session with 2 lifts."""
    algorithm_name = request.algorithm if request and request.algorithm else DEFAULT_ALGORITHM
    max_floors = request.max_floors if request and request.max_floors else 10
    session_id = session_manager.create_session(algorithm_name=algorithm_name, max_floors=max_floors)
    return {
        "session_id": session_id,
        "algorithm": algorithm_name,
        "max_floors": max_floors,
        "type": "single",
    }


@router.post("/create-comparison")
async def create_comparison(request: CreateComparisonRequest | None = None) -> dict:
    """Create a comparison session with 2 buildings, each with 2 lifts."""
    algo1 = request.algorithm1 if request and request.algorithm1 else DEFAULT_ALGORITHM
    algo2 = request.algorithm2 if request and request.algorithm2 else DEFAULT_ALGORITHM
    max_floors = request.max_floors if request and request.max_floors else 10
    session_id = session_manager.create_comparison_session(
        algorithm1=algo1, algorithm2=algo2, max_floors=max_floors
    )
    return {
        "session_id": session_id,
        "algorithm1": algo1,
        "algorithm2": algo2,
        "max_floors": max_floors,
        "type": "comparison",
    }


@router.post("/{session_id}/add-passenger")
async def add_passenger(session_id: str, request: PassengerRequest) -> dict:
    """Add a passenger request."""
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    controller.add_request(
        passenger_id=request.passenger_id,
        from_level=request.from_level,
        to_level=request.to_level,
    )
    return {"message": "Request added"}


@router.get("/{session_id}/state")
async def get_state(session_id: str) -> dict:
    """Get current simulation state."""
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    session_type = session_manager.get_session_type(session_id)

    try:
        state = controller.get_state()

        if session_type == "comparison":
            return {
                "type": "comparison",
                "building1": transform_building_state(state["building1"]),
                "building2": transform_building_state(state["building2"]),
                "global_tick": state["global_tick"],
            }
        else:
            return {"type": "single", **transform_building_state(state)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get state: {e!s}") from e


def transform_building_state(state: dict) -> dict:
    """Transform building state for API response."""
    return {
        "algorithm": state.get("algorithm"),
        "lift_a": transform_lift_state(state.get("lift_a", {})),
        "lift_b": transform_lift_state(state.get("lift_b", {})),
        "active_passengers": state.get("active_passengers", []),
        "global_tick": state.get("global_tick", 0),
        "stats": state.get("stats", {"avg_wait": 0, "avg_ride": 0, "avg_total": 0, "completed": 0}),
    }


def transform_lift_state(state: dict) -> dict:
    """Transform individual lift state for API response."""
    pending_stops = state.get("pending_stops", {})

    transformed_stops: dict = {}
    for level, actions in pending_stops.items():
        stop_infos = []
        for action_tuple in actions:
            action_type = action_tuple[0]
            passenger_id = action_tuple[1]
            to_level = action_tuple[2] if len(action_tuple) > 2 else None
            stop_infos.append({
                "passenger_id": passenger_id,
                "type": action_type,
                "to_level": to_level,
            })
        transformed_stops[level] = stop_infos

    return {
        "level": state.get("level", 0),
        "direction": state.get("direction", "idle"),
        "passengers": state.get("passengers", []),
        "stops": transformed_stops,
    }


@router.post("/{session_id}/move")
async def move_lift(session_id: str) -> dict:
    """Advance simulation by one tick."""
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    return controller.move()
