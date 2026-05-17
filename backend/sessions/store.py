from __future__ import annotations

import json
import uuid
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent.parent / "data" / "sessions"


class SessionStore:
    def __init__(self):
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._write(session_id, {"id": session_id, "messages": [], "memory": {}})
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        path = SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        if session is None:
            return
        session["messages"].append({"role": role, "content": content})
        self._write(session_id, session)

    def update_memory(self, session_id: str, memory: dict):
        session = self.get_session(session_id)
        if session is None:
            return
        session["memory"] = memory
        self._write(session_id, session)

    def list_sessions(self) -> list[dict]:
        sessions = []
        for path in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            data = json.loads(path.read_text())
            sessions.append({
                "id": data["id"],
                "message_count": len(data.get("messages", [])),
                "first_message": data["messages"][0]["content"][:50] if data.get("messages") else None,
            })
        return sessions

    def _write(self, session_id: str, data: dict):
        path = SESSIONS_DIR / f"{session_id}.json"
        path.write_text(json.dumps(data, indent=2))
