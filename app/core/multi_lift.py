"""
Multi-Building Controller for comparing different algorithms.
Each building has 2 lifts working together.
Same passengers go to both buildings for fair comparison.
"""
from app.core.building import BuildingController


class MultiBuildingController:
    """
    Comparison testbed with 2 buildings.
    Each building has 2 lifts using the same algorithm.
    Same passenger requests sent to both buildings for fair comparison.
    """

    def __init__(self, algorithm1: str = "scan", algorithm2: str = "scan") -> None:
        self.building1 = BuildingController(algorithm_name=algorithm1)
        self.building2 = BuildingController(algorithm_name=algorithm2)
        self.global_tick: int = 0

    def add_request(self, passenger_id: str, from_level: int, to_level: int) -> None:
        """Add the same passenger request to both buildings."""
        self.building1.add_request(passenger_id, from_level, to_level)
        self.building2.add_request(passenger_id, from_level, to_level)

    def move(self) -> dict:
        """Move all lifts in both buildings."""
        self.global_tick += 1
        self.building1.move()
        self.building2.move()
        return self.get_state()

    def get_state(self) -> dict:
        """Get combined state of both buildings."""
        state1 = self.building1.get_state()
        state2 = self.building2.get_state()

        return {
            "building1": state1,
            "building2": state2,
            "global_tick": self.global_tick,
        }
