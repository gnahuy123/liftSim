from fastapi import APIRouter, HTTPException
from app.core.sessions import session_manager
from app.models.schemas import PassengerRequest, LiftState

router = APIRouter()

@router.post("/create-session")
async def create_session():
    session_id = session_manager.create_session()
    return {"session_id": session_id}

@router.post("/{session_id}/add-passenger")
async def add_passenger(session_id: str, request: PassengerRequest):
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    
    controller.add_request(
        passenger_id=request.passenger_id,
        from_level=request.from_level,
        to_level=request.to_level
    )
    return {"message": "Request added"}

#improve logging
@router.get("/{session_id}/state", response_model=LiftState)
async def get_state(session_id: str):
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    
    try:
        state = controller.get_state()
        
        # Transform stops from tuples to passenger ID lists
        transformed_stops = {}
        for level, actions in state["pending_stops"].items():
            passenger_ids = []
            for action_tuple in actions:
                if len(action_tuple) >= 2:  # Has at least action and passenger_id
                    passenger_ids.append(action_tuple[1])  # Extract passenger_id
            transformed_stops[level] = passenger_ids
        
        return LiftState(
            current_level=state["level"],
            direction=state["direction"],
            passengers=state["passengers"],
            stops=transformed_stops
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get state: {str(e)}")
    
@router.post("/{session_id}/move")
async def move_lift(session_id: str):
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    
    return controller.move()