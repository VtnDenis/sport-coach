from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

from backend.agent import create_coach_agent
from backend.config import settings
from backend.sessions.store import SessionStore
from backend.services.strava_client import StravaClient
from backend.services.garmin_client import GarminClient

app = FastAPI(title="Sport Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = create_coach_agent()
session_service = InMemorySessionService()
session_store = SessionStore()
strava_client = StravaClient()
garmin_client = GarminClient()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "strava_configured": settings.strava_configured,
        "garmin_configured": settings.garmin_configured,
        "deepseek_configured": settings.deepseek_configured,
    }


@app.post("/api/sessions")
async def create_session():
    session_id = session_store.create_session()
    return {"session_id": session_id}


@app.get("/api/sessions")
async def list_sessions():
    return {"sessions": session_store.list_sessions()}


@app.post("/api/chat/{session_id}")
async def chat(session_id: str, request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    if not user_message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    session_data = session_store.get_session(session_id)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session_store.add_message(session_id, "user", user_message)

    runner = Runner(
        app_name="sport-coach",
        agent=agent,
        session_service=session_service,
    )

    async def event_stream() -> AsyncGenerator[str, None]:
        user_content = user_message
        partial_response = []

        try:
            async for event in runner.run_async(
                user_id="default",
                session_id=session_id,
                new_message=user_content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            partial_response.append(part.text)
                            yield f"data: {json.dumps({'type': 'text', 'content': part.text})}\n\n"

                if event.is_final_response():
                    full = "".join(partial_response)
                    session_store.add_message(session_id, "assistant", full)
                    session_data = session_store.get_session(session_id)
                    if session_data:
                        yield f"data: {json.dumps({'type': 'done', 'content': full})}\n\n"
                    return

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/dashboard/summary")
async def dashboard_summary():
    activities = strava_client.get_recent_activities(limit=5)
    garmin_health = garmin_client.get_health_snapshot()
    garmin_sleep = garmin_client.get_sleep_data()
    garmin_status = garmin_client.get_training_status()

    return {
        "recent_activities": activities,
        "health": garmin_health,
        "sleep": garmin_sleep,
        "training_status": garmin_status,
    }


@app.get("/api/dashboard/activities")
async def dashboard_activities(limit: int = 10, source: str = "strava"):
    if source == "garmin":
        result = garmin_client.get_activity_list(limit)
    else:
        result = strava_client.get_recent_activities(limit)
    return {"activities": result}


@app.get("/api/dashboard/health")
async def dashboard_health():
    health = garmin_client.get_health_snapshot()
    sleep = garmin_client.get_sleep_data()
    hr = garmin_client.get_heart_rate()
    return {"health": health, "sleep": sleep, "heart_rate": hr}
