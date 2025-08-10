class LiftController:
    def __init__(self):
        self.current_level = 0
        self.direction = "idle"
        self.passengers = []
        self.stops = {}
        self.history = []

    def add_request(self, passenger_id: str, from_level: int, to_level: int):
        self.stops.setdefault(from_level, []).append(("pickup", passenger_id, to_level))
        self.stops.setdefault(to_level, []).append(("dropoff", passenger_id))
        
        # Sort stops for efficiency
        self.stops = dict(sorted(self.stops.items()))

    def move(self):
        # Determine direction if idle
        if self.direction == "idle" and self.stops:
            next_level = min(self.stops.keys()) if self.current_level > min(self.stops.keys()) else max(self.stops.keys())
            self.direction = "up" if self.current_level < next_level else "down"

        # Move lift
        if self.direction == "up":
            self.current_level += 1
        elif self.direction == "down":
            self.current_level -= 1

        # Process current floor
        events = []
        if self.current_level in self.stops:
            for action, *args in self.stops[self.current_level][:]:
                if action == "pickup":
                    passenger_id, to_level = args
                    self.passengers.append(passenger_id)
                    events.append(f"Picked up {passenger_id}")
                else:  # dropoff
                    passenger_id = args[0]
                    if passenger_id in self.passengers:
                        self.passengers.remove(passenger_id)
                        events.append(f"Dropped off {passenger_id}")
            
            del self.stops[self.current_level]

        # Update direction
        if not self.stops:
            self.direction = "idle"
        elif self.direction == "up" and self.current_level >= max(self.stops.keys()):
            self.direction = "down"
        elif self.direction == "down" and self.current_level <= min(self.stops.keys()):
            self.direction = "up"

        # Log state
        state = {
            "level": self.current_level,
            "direction": self.direction,
            "passengers": self.passengers.copy(),
            "events": events
        }
        self.history.append(state)
        return state

    def get_state(self):
        return {
            "level": self.current_level,
            "direction": self.direction,
            "passengers": self.passengers.copy(),
            "pending_stops": self.stops 
        }