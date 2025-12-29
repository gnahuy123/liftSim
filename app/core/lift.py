from app.core.algorithms import ScanAlgorithm, LiftAlgorithm, get_algorithm

class LiftController:
    def __init__(self, algorithm_name: str = "scan"):
        self.current_level = 0
        self.direction = "idle"
        self.passengers = [] # IDs inside lift
        self.stops = {}
        self.history = []
        self.algorithm = get_algorithm(algorithm_name)
        self.algorithm_name = algorithm_name
        
        # Track all active requests: {pid: {"id": pid, "from": f, "to": t, "status": "WAITING"}}
        self.active_requests = {}
        # Keep recent completed for UI feedback
        self.recent_completed = [] 
        
        # Stats tracking
        self.stats_sums = {
            "wait_time": 0.0,
            "ride_time": 0.0,
            "total_time": 0.0
        }
        self.stats_counts = {
            "picked_up": 0,
            "completed": 0
        }
        
        self.global_tick = 0

    def add_request(self, passenger_id: str, from_level: int, to_level: int):
        self.stops.setdefault(from_level, []).append(("pickup", passenger_id, to_level))
        self.stops.setdefault(to_level, []).append(("dropoff", passenger_id))
        
        # Sort stops for efficiency
        self.stops = dict(sorted(self.stops.items()))
        
        # Track status
        self.active_requests[passenger_id] = {
            "passenger_id": passenger_id,
            "from_level": from_level,
            "to_level": to_level,
            "status": "WAITING",
            "created_at": self.global_tick,
            "picked_up_at": None,
            "completed_at": None
        }

    def move(self):
        self.global_tick += 1
        
        # 1. Process current floor
        events = []
        if self.current_level in self.stops:
            remaining_actions = []
            for action_tuple in self.stops[self.current_level]:
                action = action_tuple[0]
                args = action_tuple[1:]
                
                if action == "pickup":
                    passenger_id, to_level = args
                    self.passengers.append(passenger_id)
                    events.append(f"Picked up {passenger_id}")
                    if passenger_id in self.active_requests:
                        self.active_requests[passenger_id]["status"] = "MOVING"
                        self.active_requests[passenger_id]["picked_up_at"] = self.global_tick
                        
                        # Update Wait Time Stat
                        p_data = self.active_requests[passenger_id]
                        wait_time = p_data["picked_up_at"] - p_data["created_at"]
                        self.stats_sums["wait_time"] += wait_time
                        self.stats_counts["picked_up"] += 1
                        
                else:  # dropoff
                    passenger_id = args[0]
                    if passenger_id in self.passengers:
                        self.passengers.remove(passenger_id)
                        events.append(f"Dropped off {passenger_id}")
                        if passenger_id in self.active_requests:
                            self.active_requests[passenger_id]["status"] = "ARRIVED"
                            self.active_requests[passenger_id]["completed_at"] = self.global_tick
                            
                            # Update stats
                            p_data = self.active_requests[passenger_id]
                            # Ride Time
                            ride_time = p_data["completed_at"] - p_data["picked_up_at"]
                            self.stats_sums["ride_time"] += ride_time
                            
                            # Total Time
                            total_time = p_data["completed_at"] - p_data["created_at"]
                            self.stats_sums["total_time"] += total_time
                            
                            self.stats_counts["completed"] += 1
                            
                            # Move to recent completed and remove from active
                            self.recent_completed.append(p_data)
                            if len(self.recent_completed) > 10: # Keep last 10
                                self.recent_completed.pop(0)
                            
                            del self.active_requests[passenger_id]
                            
                            pass
                    else:
                        # Passenger not here yet (e.g. rounded trip). Keep the stop.
                        remaining_actions.append(action_tuple)
            
            if remaining_actions:
                self.stops[self.current_level] = remaining_actions
            else:
                del self.stops[self.current_level]

        # 2. Determine/Update Direction using Algorithm
        self.direction = self.algorithm.pick_next_direction(
            self.current_level, 
            self.direction, 
            self.stops
        )

        # 3. Move lift
        if self.direction == "up":
            self.current_level += 1
        elif self.direction == "down":
            self.current_level -= 1
        
        # Log state
        state = self.get_state()
        state["events"] = events
        self.history.append(state)
        return state

    def get_state(self):
        # Calculate averages
        avg_wait = self.stats_sums["wait_time"] / self.stats_counts["picked_up"] if self.stats_counts["picked_up"] > 0 else 0
        avg_ride = self.stats_sums["ride_time"] / self.stats_counts["completed"] if self.stats_counts["completed"] > 0 else 0
        avg_total = self.stats_sums["total_time"] / self.stats_counts["completed"] if self.stats_counts["completed"] > 0 else 0
        
        # Combine active and recent completed for the view
        # We return a list of values
        all_visible = list(self.active_requests.values()) + self.recent_completed

        return {
            "level": self.current_level,
            "direction": self.direction,
            "passengers": self.passengers.copy(),
            "pending_stops": self.stops,
            "active_passengers": all_visible,
            "global_tick": self.global_tick,
            "stats": {
                "avg_wait": avg_wait,
                "avg_ride": avg_ride,
                "avg_total": avg_total
            }
        }

