"""
Lift Controller - manages a single lift's state and movement.
"""
from app.core.algorithms import get_algorithm
from app.core.config import DEFAULT_ALGORITHM, MAX_FLOORS, MIN_FLOOR


class LiftController:
    """Single lift controller with encapsulated state access."""

    def __init__(
        self, algorithm_name: str = DEFAULT_ALGORITHM, max_floors: int = MAX_FLOORS
    ) -> None:
        self.current_level: int = MIN_FLOOR
        self.max_floors: int = max_floors
        self.direction: str = "idle"
        self.passengers: list[str] = []
        self.stops: dict[int, list[tuple]] = {}
        self.history: list[dict] = []
        self.algorithm = get_algorithm(algorithm_name)
        self.algorithm_name: str = algorithm_name

        self.active_requests: dict[str, dict] = {}
        self.recent_completed: list[dict] = []

        self.stats_sums: dict[str, float] = {
            "wait_time": 0.0,
            "ride_time": 0.0,
            "total_time": 0.0,
        }
        self.stats_counts: dict[str, int] = {
            "picked_up": 0,
            "completed": 0,
        }

        self.global_tick: int = 0

    # === Law of Demeter: Encapsulated accessors ===

    def get_load(self) -> int:
        """Get total load: passengers inside + pending requests."""
        return len(self.passengers) + len(self.active_requests)

    def get_distance_to(self, floor: int) -> int:
        """Get distance from current level to target floor."""
        return abs(self.current_level - floor)

    def get_passenger_count(self) -> int:
        """Get number of passengers currently inside the lift."""
        return len(self.passengers)

    # === Request handling ===

    def add_request(self, passenger_id: str, from_level: int, to_level: int) -> None:
        """Add a passenger request."""
        self.stops.setdefault(from_level, []).append(("pickup", passenger_id, to_level))
        self.stops.setdefault(to_level, []).append(("dropoff", passenger_id))
        self.stops = dict(sorted(self.stops.items()))

        self.active_requests[passenger_id] = {
            "passenger_id": passenger_id,
            "from_level": from_level,
            "to_level": to_level,
            "status": "WAITING",
            "created_at": self.global_tick,
            "picked_up_at": None,
            "completed_at": None,
        }

    # === Movement ===

    def move(self) -> dict:
        """Advance simulation by one tick."""
        self.global_tick += 1

        events = self._process_stops()
        self._update_direction()
        self._move_lift()

        state = self.get_state()
        state["events"] = events
        self.history.append(state)
        return state

    def _process_stops(self) -> list[str]:
        """Process pickups and dropoffs at current level."""
        events: list[str] = []

        if self.current_level not in self.stops:
            return events

        remaining_actions: list[tuple] = []

        for action_tuple in self.stops[self.current_level]:
            action = action_tuple[0]
            args = action_tuple[1:]

            if action == "pickup":
                events.extend(self._handle_pickup(args[0], args[1]))
            else:
                result = self._handle_dropoff(args[0])
                if result is None:
                    remaining_actions.append(action_tuple)
                else:
                    events.extend(result)

        if remaining_actions:
            self.stops[self.current_level] = remaining_actions
        else:
            del self.stops[self.current_level]

        return events

    def _handle_pickup(self, passenger_id: str, to_level: int) -> list[str]:
        """Handle passenger pickup."""
        self.passengers.append(passenger_id)

        if passenger_id in self.active_requests:
            self.active_requests[passenger_id]["status"] = "MOVING"
            self.active_requests[passenger_id]["picked_up_at"] = self.global_tick

            wait_time = self.global_tick - self.active_requests[passenger_id]["created_at"]
            self.stats_sums["wait_time"] += wait_time
            self.stats_counts["picked_up"] += 1

        return [f"Picked up {passenger_id}"]

    def _handle_dropoff(self, passenger_id: str) -> list[str] | None:
        """Handle passenger dropoff. Returns None if passenger not in lift."""
        if passenger_id not in self.passengers:
            return None

        self.passengers.remove(passenger_id)

        if passenger_id in self.active_requests:
            p_data = self.active_requests[passenger_id]
            p_data["status"] = "ARRIVED"
            p_data["completed_at"] = self.global_tick

            ride_time = p_data["completed_at"] - p_data["picked_up_at"]
            total_time = p_data["completed_at"] - p_data["created_at"]

            self.stats_sums["ride_time"] += ride_time
            self.stats_sums["total_time"] += total_time
            self.stats_counts["completed"] += 1

            self.recent_completed.append(p_data)
            if len(self.recent_completed) > 10:
                self.recent_completed.pop(0)

            del self.active_requests[passenger_id]

        return [f"Dropped off {passenger_id}"]

    def _update_direction(self) -> None:
        """Update direction using the algorithm."""
        # Filter stops to only include fulfillable actions:
        # 1. Any pickup
        # 2. Dropoff for someone already in the lift
        fulfillable_stops = {}
        for level, actions in self.stops.items():
            valid_actions = [
                a for a in actions
                if a[0] == "pickup" or (a[0] == "dropoff" and a[1] in self.passengers)
            ]
            if valid_actions:
                fulfillable_stops[level] = valid_actions

        self.direction = self.algorithm.pick_next_direction(
            self.current_level, self.direction, fulfillable_stops
        )

    def _move_lift(self) -> None:
        """Move the lift based on current direction."""
        if self.direction == "up" and self.current_level < MAX_FLOORS:
            self.current_level += 1
        elif self.direction == "down" and self.current_level > MIN_FLOOR:
            self.current_level -= 1

    # === State ===

    def get_state(self) -> dict:
        """Get current lift state."""
        avg_wait = (
            self.stats_sums["wait_time"] / self.stats_counts["picked_up"]
            if self.stats_counts["picked_up"] > 0
            else 0
        )
        avg_ride = (
            self.stats_sums["ride_time"] / self.stats_counts["completed"]
            if self.stats_counts["completed"] > 0
            else 0
        )
        avg_total = (
            self.stats_sums["total_time"] / self.stats_counts["completed"]
            if self.stats_counts["completed"] > 0
            else 0
        )

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
                "avg_total": avg_total,
            },
        }
