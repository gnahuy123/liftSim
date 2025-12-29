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
        
        # Transform stops from tuples to StopInfo objects
        transformed_stops = {}
        for level, actions in state["pending_stops"].items():
            stop_infos = []
            for action_tuple in actions:
                # Expected tuple: (action_type, passenger_id, [to_level])
                action_type = action_tuple[0]
                passenger_id = action_tuple[1]
                to_level = action_tuple[2] if len(action_tuple) > 2 else None
                
                stop_infos.append({
                    "passenger_id": passenger_id,
                    "type": action_type,
                    "to_level": to_level
                })
            transformed_stops[level] = stop_infos
        
        return LiftState(
            current_level=state["level"],
            direction=state["direction"],
            passengers=state["passengers"],
            stops=transformed_stops,
            active_passengers=state.get("active_passengers", []),
            global_tick=state.get("global_tick", 0),
            stats=state.get("stats")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get state: {str(e)}")
    
@router.post("/{session_id}/move")
async def move_lift(session_id: str):
    controller = session_manager.get_controller(session_id)
    if not controller:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    
    return controller.move()