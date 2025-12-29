from abc import ABC, abstractmethod


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


class ShortestSeekAlgorithm(LiftAlgorithm):
    """
    SSTF (Shortest Seek Time First).
    Always moves to the nearest requested floor, regardless of direction.
    Efficient for throughput but can lead to starvation.
    """
    name = "sstf"
    description = "SSTF - Always moves to the nearest requested floor"

    def pick_next_direction(self, current_level: int, current_direction: str, stops: dict) -> str:
        if not stops:
            return "idle"

        # Find the floor with the minimum distance
        nearest_floor = min(stops.keys(), key=lambda f: abs(f - current_level))

        if nearest_floor > current_level:
            return "up"
        elif nearest_floor < current_level:
            return "down"
        return "idle"


class NearestNeighborAlgorithm(LiftAlgorithm):
    """
    Nearest Neighbor with Momentum.
    Primarily moves to the nearest floor, but if multiple floors are at equal distance,
    prefers the one in the current direction.
    """
    name = "nearest"
    description = "Nearest Neighbor - Closest stop with direction preference"

    def pick_next_direction(self, current_level: int, current_direction: str, stops: dict) -> str:
        if not stops:
            return "idle"

        floors = list(stops.keys())
        distances = [abs(f - current_level) for f in floors]
        min_dist = min(distances)

        candidates = [f for f in floors if abs(f - current_level) == min_dist]

        if len(candidates) == 1:
            target = candidates[0]
        else:
            # If equal distance, keep current direction if possible
            if current_direction == "up" and any(f > current_level for f in candidates):
                target = min(f for f in candidates if f > current_level)
            elif current_direction == "down" and any(f < current_level for f in candidates):
                target = max(f for f in candidates if f < current_level)
            else:
                target = candidates[0]

        if target > current_level:
            return "up"
        elif target < current_level:
            return "down"
        return "idle"


# Algorithm Registry - maps name to class
# New algorithms can be added here
ALGORITHM_REGISTRY: dict[str, type[LiftAlgorithm]] = {
    "scan": ScanAlgorithm,
    "sstf": ShortestSeekAlgorithm,
    "nearest": NearestNeighborAlgorithm,
}


def get_available_algorithms() -> list[dict]:
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
