"""
Tests for lift scheduling algorithms.
Verifies that no passenger waits infinitely and all passengers eventually reach destination.
"""
import pytest
import random
from app.core.lift import LiftController
from app.core.building import BuildingController
from app.core.algorithms import get_available_algorithms, ALGORITHM_REGISTRY
from app.core.config import MAX_FLOORS, MIN_FLOOR


class TestAlgorithmNoInfiniteWait:
    """Test that algorithms don't leave any passenger waiting forever."""

    @pytest.fixture(params=list(ALGORITHM_REGISTRY.keys()))
    def algorithm_name(self, request):
        return request.param

    def test_single_passenger_completes(self, algorithm_name):
        """A single passenger should always complete their journey."""
        controller = LiftController(algorithm_name=algorithm_name)
        controller.add_request("P001", 0, MAX_FLOORS)

        max_moves = 50
        for _ in range(max_moves):
            controller.move()
            if "P001" not in controller.active_requests:
                break

        assert "P001" not in controller.active_requests, \
            f"Passenger P001 did not complete with {algorithm_name} algorithm"

    def test_two_passengers_opposite_directions(self, algorithm_name):
        """Two passengers going opposite directions should both complete."""
        controller = LiftController(algorithm_name=algorithm_name)
        controller.add_request("P001", 0, MAX_FLOORS)
        controller.add_request("P002", MAX_FLOORS, 0)

        max_moves = 100
        for _ in range(max_moves):
            controller.move()
            if not controller.active_requests:
                break

        assert not controller.active_requests, \
            f"Not all passengers completed with {algorithm_name}: {list(controller.active_requests.keys())}"

    def test_random_passengers_all_complete(self, algorithm_name):
        """Random passengers should all eventually complete."""
        random.seed(42)
        controller = LiftController(algorithm_name=algorithm_name)

        num_passengers = 20
        for i in range(num_passengers):
            from_level = random.randint(MIN_FLOOR, MAX_FLOORS)
            to_level = random.randint(MIN_FLOOR, MAX_FLOORS)
            while to_level == from_level:
                to_level = random.randint(MIN_FLOOR, MAX_FLOORS)
            controller.add_request(f"P{i:03d}", from_level, to_level)

        max_moves = 500
        for _ in range(max_moves):
            controller.move()
            if not controller.active_requests:
                break

        assert not controller.active_requests, \
            f"Passengers remaining with {algorithm_name}: {list(controller.active_requests.keys())}"


class TestEdgeCases:
    """Test edge cases for lift behavior."""

    def test_pickup_on_current_floor(self):
        """Passenger waiting on current floor should be picked up immediately."""
        controller = LiftController(algorithm_name="scan")
        controller.current_level = 5

        controller.add_request("P001", 5, 10)
        controller.move()

        # After one move, passenger should be picked up (MOVING status)
        assert "P001" in controller.passengers

    def test_multiple_pickups_same_floor(self):
        """Multiple passengers on same floor should all be picked up."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)
        controller.add_request("P002", 0, 8)
        controller.add_request("P003", 0, 3)

        controller.move()

        assert len(controller.passengers) == 3

    def test_multiple_dropoffs_same_floor(self):
        """Multiple passengers going to same floor should all be dropped off."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)
        controller.add_request("P002", 1, 5)

        # Move until we reach floor 5
        for _ in range(20):
            controller.move()
            if not controller.active_requests:
                break

        assert not controller.active_requests

    def test_round_trip_passenger(self):
        """Passenger can make a round trip."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)

        # First trip
        for _ in range(15):
            controller.move()
            if "P001" not in controller.active_requests:
                break

        assert "P001" not in controller.active_requests

        # Second trip back
        controller.add_request("P001", 5, 0)
        for _ in range(15):
            controller.move()
            if "P001" not in controller.active_requests:
                break

        assert "P001" not in controller.active_requests


class TestBuildingController:
    """Tests for 2-lift building controller."""

    def test_dispatch_distributes_load(self):
        """Dispatch should distribute passengers across both lifts."""
        building = BuildingController(algorithm_name="scan")

        # Add 4 passengers all from floor 0
        for i in range(4):
            building.add_request(f"P{i:03d}", 0, 5 + i)

        # Should be split between lifts
        lift_a_load = building.lift_a.get_load()
        lift_b_load = building.lift_b.get_load()

        assert lift_a_load > 0
        assert lift_b_load > 0
        assert lift_a_load + lift_b_load == 4

    def test_dispatch_prefers_closer_lift(self):
        """Dispatch should prefer closer lift for pickup."""
        building = BuildingController(algorithm_name="scan")

        # Move lift_a to floor 5
        building.lift_a.current_level = 5

        # Request from floor 8 should go to lift_a (closer)
        building.add_request("P001", 8, 0)

        assert building.lift_a.get_load() == 1
        assert building.lift_b.get_load() == 0


class TestAlgorithmBehavior:
    """Test that each algorithm exhibits expected behavior."""

    def test_all_algorithms_registered(self):
        """All expected algorithms should be in registry."""
        algos = get_available_algorithms()
        names = [a["name"] for a in algos]
        assert "scan" in names

    def test_scan_continues_direction(self):
        """SCAN should continue in direction until no more requests."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 5, 10)
        controller.add_request("P002", 2, 0)

        controller.move()
        assert controller.direction == "up"


class TestLiftControllerIntegration:
    """Integration tests for the lift controller."""

    def test_stats_calculated_correctly(self):
        """Stats should be calculated after passengers complete."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)

        for _ in range(20):
            controller.move()
            if not controller.active_requests:
                break

        state = controller.get_state()
        assert state["stats"]["avg_total"] > 0

    def test_algorithm_name_stored(self):
        """Controller should store the algorithm name."""
        controller = LiftController(algorithm_name="scan")
        assert controller.algorithm_name == "scan"

    def test_get_load_method(self):
        """get_load should return passengers inside + active requests."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)
        controller.add_request("P002", 0, 8)

        # Before move: 0 passengers inside, 2 in active_requests
        assert controller.get_load() == 2
        assert controller.get_passenger_count() == 0

        controller.move()  # Pick up passengers

        # After move: 2 passengers inside, 2 still in active_requests (MOVING)
        # get_load counts both, get_passenger_count only counts inside
        assert controller.get_passenger_count() == 2

    def test_get_distance_to_method(self):
        """get_distance_to should return correct distance."""
        controller = LiftController(algorithm_name="scan")
        controller.current_level = 5

        assert controller.get_distance_to(5) == 0
        assert controller.get_distance_to(0) == 5
        assert controller.get_distance_to(10) == 5
