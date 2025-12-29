"""
Session management for lift simulation.
"""
import uuid
from datetime import datetime, timedelta

from app.core.building import BuildingController
from app.core.multi_lift import MultiBuildingController


class SessionManager:
    """Manages simulation sessions."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict] = {}
        self.session_timeout: timedelta = timedelta(minutes=30)

    def create_session(self, algorithm_name: str = "scan") -> str:
        """Create a single-building session with 2 lifts."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "type": "single",
            "controller": BuildingController(algorithm_name=algorithm_name),
            "last_activity": datetime.now(),
        }
        return session_id

    def create_comparison_session(
        self, algorithm1: str = "scan", algorithm2: str = "scan"
    ) -> str:
        """Create a comparison session with 2 buildings, each having 2 lifts."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "type": "comparison",
            "controller": MultiBuildingController(algorithm1=algorithm1, algorithm2=algorithm2),
            "last_activity": datetime.now(),
        }
        return session_id

    def get_controller(
        self, session_id: str
    ) -> BuildingController | MultiBuildingController | None:
        """Get controller for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
            return self.sessions[session_id]["controller"]
        return None

    def get_session_type(self, session_id: str) -> str | None:
        """Get the type of session (single or comparison)."""
        if session_id in self.sessions:
            return self.sessions[session_id].get("type", "single")
        return None

    def cleanup_sessions(self) -> None:
        """Remove expired sessions."""
        expired: list[str] = []
        for session_id, data in self.sessions.items():
            if datetime.now() - data["last_activity"] > self.session_timeout:
                expired.append(session_id)

        for session_id in expired:
            del self.sessions[session_id]


# Global session manager instance
session_manager = SessionManager()
