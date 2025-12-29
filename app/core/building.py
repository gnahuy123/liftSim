"""
Building Controller - Manages 2 lifts servicing the same building.
Implements dispatch logic to assign incoming requests to one of the lifts.
"""
from app.core.lift import LiftController


class BuildingController:
    """
    A building with 2 lifts working together to service passengers.
    Uses dispatch logic to assign each request to the most suitable lift.
    """
    
    def __init__(self, algorithm_name: str = "scan"):
        self.lift_a = LiftController(algorithm_name=algorithm_name)
        self.lift_b = LiftController(algorithm_name=algorithm_name)
        self.algorithm_name = algorithm_name
        self.global_tick = 0
        
        # Stats tracking
        self.total_passengers = 0
        self.completed_passengers = 0
    
    def add_request(self, passenger_id: str, from_level: int, to_level: int):
        """
        Add a passenger request. Dispatch to the most suitable lift.
        Uses dispatch logic: closest lift wins, tie-break by fewer total requests.
        """
        # Simple dispatch: choose lift closest to pickup floor
        dist_a = abs(self.lift_a.current_level - from_level)
        dist_b = abs(self.lift_b.current_level - from_level)
        
        # Count total requests (inside + pending)
        load_a = len(self.lift_a.passengers) + len(self.lift_a.active_requests)
        load_b = len(self.lift_b.passengers) + len(self.lift_b.active_requests)
        
        # Prefer closer lift, or less loaded if equal distance
        if dist_a < dist_b:
            target_lift = self.lift_a
            suffix = "_A"
        elif dist_b < dist_a:
            target_lift = self.lift_b
            suffix = "_B"
        elif load_a <= load_b:
            target_lift = self.lift_a
            suffix = "_A"
        else:
            target_lift = self.lift_b
            suffix = "_B"
        
        target_lift.add_request(f"{passenger_id}{suffix}", from_level, to_level)
        self.total_passengers += 1
    
    def move(self):
        """Move both lifts one step."""
        self.global_tick += 1
        state_a = self.lift_a.move()
        state_b = self.lift_b.move()
        return {
            "lift_a": state_a,
            "lift_b": state_b,
            "global_tick": self.global_tick
        }
    
    def get_state(self):
        """Get combined state of both lifts."""
        state_a = self.lift_a.get_state()
        state_b = self.lift_b.get_state()
        
        # Count completed from both lifts
        completed_a = self.lift_a.stats_counts["completed"]
        completed_b = self.lift_b.stats_counts["completed"]
        total_completed = completed_a + completed_b
        
        # Calculate combined averages
        if total_completed > 0:
            avg_wait = (state_a["stats"]["avg_wait"] * completed_a + 
                       state_b["stats"]["avg_wait"] * completed_b) / total_completed
            avg_ride = (state_a["stats"]["avg_ride"] * completed_a + 
                       state_b["stats"]["avg_ride"] * completed_b) / total_completed
            avg_total = (state_a["stats"]["avg_total"] * completed_a + 
                        state_b["stats"]["avg_total"] * completed_b) / total_completed
        else:
            avg_wait = avg_ride = avg_total = 0
        
        return {
            "algorithm": self.algorithm_name,
            "lift_a": {
                "level": self.lift_a.current_level,
                "direction": self.lift_a.direction,
                "passengers": self.lift_a.passengers,
                "pending_stops": self.lift_a.stops,
            },
            "lift_b": {
                "level": self.lift_b.current_level,
                "direction": self.lift_b.direction,
                "passengers": self.lift_b.passengers,
                "pending_stops": self.lift_b.stops,
            },
            "active_passengers": state_a["active_passengers"] + state_b["active_passengers"],
            "global_tick": self.global_tick,
            "stats": {
                "avg_wait": avg_wait,
                "avg_ride": avg_ride,
                "avg_total": avg_total,
                "completed": total_completed
            }
        }
