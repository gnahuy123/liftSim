from abc import ABC, abstractmethod

class LiftAlgorithm(ABC):
    @abstractmethod
    def pick_next_direction(self, current_level: int, current_direction: str, stops: dict) -> str:
        """
        Determine the next direction based on current state and stops.
        Returns: "up", "down", or "idle"
        """
        pass

class ScanAlgorithm(LiftAlgorithm):
    """
    Standard Elevator Algorithm (SCAN/LOOK).
    Continues in current direction until no more requests, then switches.
    """
    def pick_next_direction(self, current_level: int, current_direction: str, stops: dict) -> str:
        if not stops:
            return "idle"
        
        if current_direction == "idle":
            # Simple heuristic: go to nearest request
            # Or just standard min/max logic
            min_stop = min(stops.keys())
            max_stop = max(stops.keys())
            
            # If we are above the lowest stop, go down to pick/drop it? 
            # Actually, standard SCAN: if any request is above, go up?
            # Let's stick to the previous logic which was robust enough:
            # Go to the nearest end?
            
            # Previous logic:
            # next_level = min(self.stops.keys()) if self.current_level > min(self.stops.keys()) else max(self.stops.keys())
            # self.direction = "up" if self.current_level < next_level else "down"
            
            if current_level > min_stop:
                return "down"
            else:
                return "up"

        elif current_direction == "up":
            # Continue up if there are stops above or at current
            # But strictly, if we are at max, we switch.
            if current_level >= max(stops.keys()):
                return "down"
            return "up"
            
        elif current_direction == "down":
            if current_level <= min(stops.keys()):
                return "up"
            return "down"
            
        return "idle"
