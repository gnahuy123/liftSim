"""
Building Controller - Manages 2 lifts servicing the same building.
Uses encapsulated accessors to follow Law of Demeter.
"""
from app.core.config import DEFAULT_ALGORITHM
from app.core.lift import LiftController


class BuildingController:
    """A building with 2 lifts working together to service passengers."""

    def __init__(self, algorithm_name: str = DEFAULT_ALGORITHM) -> None:
        self.lift_a = LiftController(algorithm_name=algorithm_name)
        self.lift_b = LiftController(algorithm_name=algorithm_name)
        self.algorithm_name: str = algorithm_name
        self.global_tick: int = 0
        self.total_passengers: int = 0

    def add_request(self, passenger_id: str, from_level: int, to_level: int) -> None:
        """Dispatch request to the most suitable lift."""
        # Use encapsulated methods instead of accessing internal state
        dist_a = self.lift_a.get_distance_to(from_level)
        dist_b = self.lift_b.get_distance_to(from_level)
        load_a = self.lift_a.get_load()
        load_b = self.lift_b.get_load()

        # Prefer closer lift, or less loaded if equal distance
        if dist_a < dist_b:
            target_lift, suffix = self.lift_a, "_A"
        elif dist_b < dist_a:
            target_lift, suffix = self.lift_b, "_B"
        elif load_a <= load_b:
            target_lift, suffix = self.lift_a, "_A"
        else:
            target_lift, suffix = self.lift_b, "_B"

        target_lift.add_request(f"{passenger_id}{suffix}", from_level, to_level)
        self.total_passengers += 1

    def move(self) -> dict:
        """Move both lifts one step."""
        self.global_tick += 1
        self.lift_a.move()
        self.lift_b.move()
        return self.get_state()

    def get_state(self) -> dict:
        """Get combined state of both lifts."""
        state_a = self.lift_a.get_state()
        state_b = self.lift_b.get_state()

        completed_a = self.lift_a.stats_counts["completed"]
        completed_b = self.lift_b.stats_counts["completed"]
        total_completed = completed_a + completed_b

        if total_completed > 0:
            avg_wait = (
                state_a["stats"]["avg_wait"] * completed_a
                + state_b["stats"]["avg_wait"] * completed_b
            ) / total_completed
            avg_ride = (
                state_a["stats"]["avg_ride"] * completed_a
                + state_b["stats"]["avg_ride"] * completed_b
            ) / total_completed
            avg_total = (
                state_a["stats"]["avg_total"] * completed_a
                + state_b["stats"]["avg_total"] * completed_b
            ) / total_completed
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
                "completed": total_completed,
            },
        }
