from abc import ABC, abstractmethod
from typing import Dict, List, Type


class LiftAlgorithm(ABC):
    """Base class for lift scheduling algorithms."""
    
    name: str = "base"
    description: str = "Base algorithm"
    
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
    This is the baseline algorithm used in most real elevators.
    """
    name = "scan"
    description = "SCAN/LOOK - Continues in direction until no more requests"
    
    def pick_next_direction(self, current_level: int, current_direction: str, stops: dict) -> str:
        if not stops:
            return "idle"
        
        if current_direction == "idle":
            min_stop = min(stops.keys())
            max_stop = max(stops.keys())
            
            if current_level > min_stop:
                return "down"
            else:
                return "up"

        elif current_direction == "up":
            if current_level >= max(stops.keys()):
                return "down"
            return "up"
            
        elif current_direction == "down":
            if current_level <= min(stops.keys()):
                return "up"
            return "down"
            
        return "idle"


# Algorithm Registry - maps name to class
# New algorithms can be added here
ALGORITHM_REGISTRY: Dict[str, Type[LiftAlgorithm]] = {
    "scan": ScanAlgorithm,
}


def get_available_algorithms() -> List[dict]:
    """Returns list of available algorithms with their metadata."""
    return [
        {
            "name": algo_class.name,
            "description": algo_class.description
        }
        for algo_class in ALGORITHM_REGISTRY.values()
    ]


def get_algorithm(name: str) -> LiftAlgorithm:
    """Get an algorithm instance by name. Defaults to ScanAlgorithm if not found."""
    algo_class = ALGORITHM_REGISTRY.get(name, ScanAlgorithm)
    return algo_class()
