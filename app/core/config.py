"""
Centralized configuration for the lift simulation.
"""
import os

# Building configuration
MAX_FLOORS: int = 10
MIN_FLOOR: int = 0

# Simulation configuration
DEFAULT_TICK_INTERVAL_MS: int = 1000  # Server-side tick interval
SESSION_TIMEOUT_MINUTES: int = 30

# CORS configuration
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8000"
).split(",")

# Algorithm defaults
DEFAULT_ALGORITHM: str = "scan"
