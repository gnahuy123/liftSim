import uuid
from datetime import datetime, timedelta
from app.core.lift import LiftController

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(minutes=30)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "controller": LiftController(),
            "last_activity": datetime.now()
        }
        return session_id

    def get_controller(self, session_id: str) -> LiftController:
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
            return self.sessions[session_id]["controller"]
        return None

    def cleanup_sessions(self):
        expired = []
        for session_id, data in self.sessions.items():
            if datetime.now() - data["last_activity"] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]

# Global session manager instance
session_manager = SessionManager()