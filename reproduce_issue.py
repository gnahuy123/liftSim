from app.core.lift import LiftController

def test_1_to_10_to_1():
    lift = LiftController()
    # Scenario: Lift at 1 (or starts 0 -> 1).
    # P1: 1 -> 10
    # P2: 10 -> 1
    
    # Let's say we add them both at start.
    lift.add_request("P1", 1, 10)
    lift.add_request("P2", 10, 1)
    
    print("\n--- Start Simulation ---")
    moved_count = 0
    while moved_count < 30:
        state = lift.move()
        print(f"Step {moved_count+1}: Level {state['level']} | Dir {state['direction']} | Pass {state['passengers']} | Stops {list(state['pending_stops'].keys())}")
        
        moved_count += 1
        
        if state['level'] == 1 and state['direction'] == 'idle' and not state['passengers']:
            print(">>> Reached Level 1 and Idle. Success.")
            break

test_1_to_10_to_1()
