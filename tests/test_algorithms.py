"""
Tests for lift scheduling algorithms.
Verifies that no passenger waits infinitely and all passengers eventually reach destination.
"""
import pytest
import random
from app.core.lift import LiftController
from app.core.algorithms import get_available_algorithms, ALGORITHM_REGISTRY


class TestAlgorithmNoInfiniteWait:
    """Test that algorithms don't leave any passenger waiting forever."""
    
    @pytest.fixture(params=["scan", "naive", "optimized"])
    def algorithm_name(self, request):
        return request.param
    
    def test_single_passenger_completes(self, algorithm_name):
        """A single passenger should always complete their journey."""
        controller = LiftController(algorithm_name=algorithm_name)
        controller.add_request("P001", 0, 10)
        
        max_moves = 50  # Should complete well before this
        for _ in range(max_moves):
            controller.move()
            if "P001" not in controller.active_requests:
                break
        
        assert "P001" not in controller.active_requests, \
            f"Passenger P001 did not complete with {algorithm_name} algorithm"
    
    def test_two_passengers_opposite_directions(self, algorithm_name):
        """Two passengers going opposite directions should both complete."""
        controller = LiftController(algorithm_name=algorithm_name)
        controller.add_request("P001", 0, 10)
        controller.add_request("P002", 10, 0)
        
        max_moves = 100
        for _ in range(max_moves):
            controller.move()
            if not controller.active_requests:
                break
        
        assert not controller.active_requests, \
            f"Not all passengers completed with {algorithm_name}: {list(controller.active_requests.keys())}"
    
    def test_random_passengers_all_complete(self, algorithm_name):
        """Random passengers should all eventually complete."""
        random.seed(42)  # Reproducible
        controller = LiftController(algorithm_name=algorithm_name)
        
        # Add 20 random passengers
        num_passengers = 20
        for i in range(num_passengers):
            from_level = random.randint(0, 10)
            to_level = random.randint(0, 10)
            while to_level == from_level:
                to_level = random.randint(0, 10)
            controller.add_request(f"P{i:03d}", from_level, to_level)
        
        # Run simulation with generous limit
        max_moves = 500
        for _ in range(max_moves):
            controller.move()
            if not controller.active_requests:
                break
        
        assert not controller.active_requests, \
            f"Passengers remaining with {algorithm_name}: {list(controller.active_requests.keys())}"
    
    def test_max_wait_time_bounded(self, algorithm_name):
        """No passenger should wait more than a reasonable time."""
        random.seed(123)
        controller = LiftController(algorithm_name=algorithm_name)
        
        # Add 10 passengers
        for i in range(10):
            from_level = random.randint(0, 10)
            to_level = random.randint(0, 10)
            while to_level == from_level:
                to_level = random.randint(0, 10)
            controller.add_request(f"P{i:03d}", from_level, to_level)
        
        max_moves = 300
        max_wait_observed = 0
        
        for _ in range(max_moves):
            controller.move()
            
            # Check wait times of still-waiting passengers
            for pid, pdata in controller.active_requests.items():
                if pdata["status"] == "WAITING":
                    current_wait = controller.global_tick - pdata["created_at"]
                    max_wait_observed = max(max_wait_observed, current_wait)
            
            if not controller.active_requests:
                break
        
        # With 11 floors, even the worst case shouldn't exceed ~110 ticks
        # (go up 10, down 10, repeat for each passenger in queue)
        max_acceptable_wait = 150
        assert max_wait_observed <= max_acceptable_wait, \
            f"Max wait {max_wait_observed} exceeds {max_acceptable_wait} with {algorithm_name}"


class TestAlgorithmBehavior:
    """Test that each algorithm exhibits expected behavior."""
    
    def test_all_algorithms_registered(self):
        """All expected algorithms should be in registry."""
        algos = get_available_algorithms()
        names = [a["name"] for a in algos]
        assert "scan" in names
        assert "naive" in names
        assert "optimized" in names
    
    def test_scan_continues_direction(self):
        """SCAN should continue in direction until no more requests."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 5, 10)
        controller.add_request("P002", 2, 0)
        
        # Lift starts at 0, should go up first to get P001
        controller.move()
        assert controller.direction == "up"
    
    def test_optimized_goes_nearest_when_idle(self):
        """Optimized should go to nearest request when idle."""
        controller = LiftController(algorithm_name="optimized")
        controller.current_level = 5  # Start in middle
        controller.add_request("P001", 8, 0)  # 3 floors away
        controller.add_request("P002", 1, 10)  # 4 floors away
        
        controller.move()
        # Should go to floor 8 (nearest), so direction should be up
        assert controller.direction == "up"


class TestLiftControllerIntegration:
    """Integration tests for the lift controller."""
    
    def test_stats_calculated_correctly(self):
        """Stats should be calculated after passengers complete."""
        controller = LiftController(algorithm_name="scan")
        controller.add_request("P001", 0, 5)
        
        # Run until passenger completes
        for _ in range(20):
            controller.move()
            if not controller.active_requests:
                break
        
        state = controller.get_state()
        assert state["stats"]["avg_total"] > 0
    
    def test_algorithm_name_stored(self):
        """Controller should store the algorithm name."""
        controller = LiftController(algorithm_name="naive")
        assert controller.algorithm_name == "naive"
