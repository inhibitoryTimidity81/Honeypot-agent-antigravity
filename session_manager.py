"""
Session Manager for Honeypot System
Manages conversation sessions, history, and extracted intelligence
"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import threading


@dataclass
class Message:
    """Represents a single message in the conversation"""
    sender: str  # "scammer" or "user"
    text: str
    timestamp: str


@dataclass
class ExtractedIntelligence:
    """Stores extracted intelligence from conversations"""
    bankAccounts: List[str] = field(default_factory=list)
    upiIds: List[str] = field(default_factory=list)
    phishingLinks: List[str] = field(default_factory=list)
    phoneNumbers: List[str] = field(default_factory=list)
    suspiciousKeywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            "bankAccounts": list(set(self.bankAccounts)),
            "upiIds": list(set(self.upiIds)),
            "phishingLinks": list(set(self.phishingLinks)),
            "phoneNumbers": list(set(self.phoneNumbers)),
            "suspiciousKeywords": list(set(self.suspiciousKeywords))
        }


@dataclass
class Session:
    """Represents a conversation session"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    intelligence: ExtractedIntelligence = field(default_factory=ExtractedIntelligence)
    scam_detected: bool = False
    agent_notes: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_completed: bool = False
    
    def add_message(self, sender: str, text: str, timestamp: str):
        """Add a message to the session"""
        self.messages.append(Message(sender=sender, text=text, timestamp=timestamp))
        self.last_activity = datetime.now()
    
    def get_engagement_duration(self) -> int:
        """Get engagement duration in seconds"""
        return int((self.last_activity - self.start_time).total_seconds())
    
    def get_total_messages(self) -> int:
        """Get total number of messages exchanged"""
        return len(self.messages)


class SessionManager:
    """Manages all conversation sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.lock = threading.Lock()
    
    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one"""
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = Session(session_id=session_id)
            return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, **kwargs):
        """Update session attributes"""
        with self.lock:
            session = self.get_or_create_session(session_id)
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
    
    def mark_completed(self, session_id: str):
        """Mark session as completed"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].is_completed = True
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours"""
        with self.lock:
            current_time = datetime.now()
            to_remove = []
            for session_id, session in self.sessions.items():
                age = (current_time - session.last_activity).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(session_id)
            
            for session_id in to_remove:
                del self.sessions[session_id]


# Global session manager instance
session_manager = SessionManager()
