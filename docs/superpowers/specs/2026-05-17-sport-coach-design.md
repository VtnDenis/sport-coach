# Sport Coach — Running Coach Chatbot Design Spec

**Date:** 2026-05-17
**Status:** Approved

## Overview

A web-based chatbot that gives running advice, stats, estimations, and coaching by connecting to the user's Strava and Garmin Connect accounts. Has memory for user preferences and history.

## Constraints

- **Web app** with React frontend
- **Free approach** — no paid services
- Single-user MVP (multi-user not in scope)

## MVP Priorities

| # | Feature | Description |
|---|---------|-------------|
| 1 | Data sync + basic Q&A | Pull activities/health, answer natural-language questions |
| 2 | Stats dashboard | Visual charts, trends, summaries |
| 3 | Proactive coaching | Analyzes data, pushes advice |
| 4 | Training plans | Generates and tracks training plans |

## Tech Stack

### LLM

- **Google ADK** (v1.x) — agent framework, tool orchestration
- **LiteLLM** — model routing layer, maps ADK to any LLM provider
- **DeepSeek** (`deepseek/deepseek-chat`) — the actual LLM, chosen for cost-free tier

> Install ADK from git main branch due to a known DeepSeek fix (issue #226).

### Data Sources

| Source | Library | License | Auth |
|--------|---------|---------|------|
| **Garmin Connect** | `python-garminconnect` (cyberjunky) | MIT | Mobile SSO → cached tokens at `~/.garminconnect/garmin_tokens.json` |
| **Strava** | `stravalib` | N/A | OAuth 2.0 |

**Garmin endpoints covered:** activities, HR, sleep, stress, body battery, training status, devices (130+ endpoints).

**Strava free tier limits:** 200 req/15min, 2000/day. Rate-limit guards required.

### Backend

- **FastAPI** — thin API layer, SSE streaming, REST endpoints
- **Uvicorn** — ASGI server

### Frontend

- **React** (Vite) — SPA
- **Chart.js** or **Recharts** — dashboard visualizations

## Architecture

Single ADK `CoachAgent` with all tools attached. FastAPI wraps the ADK Runner.

```
              React (Vite) SPA
                    │
          ┌─────────┼─────────┐
          ▼ SSE               ▼ REST/JSON
    POST /api/chat/         GET /api/dashboard/*
         {id}                     │
          │                       │
    FastAPI (main.py) ◄───────────┘
          │
    ADK Runner.run_async()
          │
    CoachAgent ──► strava_tools.py ──► strava_client.py ──► Strava API
          │    ──► garmin_tools.py ──► garmin_client.py ──► Garmin SSO
          │    ──► memory_tools.py  ──► InMemoryMemoryService
          │    ──► running_tools.py (pure Python, no API)
```

## Data Flow

### Chat (LLM-driven)

1. User types message in React → `POST /api/chat/{session_id}`
2. FastAPI relays to ADK `Runner.run_async()`
3. Agent decides which tool(s) to invoke
4. Tool function calls external API (Strava/Garmin), returns structured dict
5. LLM formulates natural-language response from tool data
6. Response streamed back via SSE to React

### Dashboard (no LLM)

1. React calls `GET /api/dashboard/summary` (or similar)
2. FastAPI directly calls Strava/Garmin tool functions (bypasses agent)
3. Returns JSON for chart rendering

### Memory

- `InMemoryMemoryService` for MVP (swappable to Postgres later)
- Agent uses `remember_fact` / `recall_information` tools via ADK `ToolContext`
- Persists user preferences, PR history, past interactions

## Tools

### Strava Tools (5)

| Tool | Returns | Idempotent |
|------|---------|------------|
| `get_recent_activities` | List[dict] of recent activities | ✓ |
| `get_activity_detail` | Full activity dict (pace, HR, splits, map) | ✓ |
| `get_athlete_stats` | YTD totals, PRs | ✓ |
| `get_training_load` | Load, freshness, fitness trend | ✓ |
| `get_segment_efforts` | Segment leaderboard, PRs | ✓ |

### Garmin Tools (5)

| Tool | Returns | Idempotent |
|------|---------|------------|
| `get_health_snapshot` | HR, stress, body battery, respiration | ✓ |
| `get_sleep_data` | Sleep stages, score, duration | ✓ |
| `get_heart_rate` | Resting/max HR, HRV | ✓ |
| `get_training_status` | Load, VO2max, recovery | ✓ |
| `get_activity_list` | List of activities with types/distances | ✓ |

### Memory Tools (3)

| Tool | Description |
|------|-------------|
| `remember_fact` | Store key-value fact in session memory |
| `recall_information` | Search/retrieve stored facts |
| `get_user_profile` | Returns structured user profile from memory |

### Running Tools (4, pure Python)

| Tool | Input | Output |
|------|-------|--------|
| `calculate_pace` | distance, time | pace per km |
| `predict_race_time` | recent race time + target distance | predicted finish time |
| `calculate_splits` | target distance, target time | per-km splits |
| `training_zones` | max HR, resting HR | HR zone ranges |

## Project Structure

```
sport-coach/
├── backend/
│   ├── main.py              # FastAPI app, routes, SSE streaming
│   ├── agent.py             # ADK CoachAgent definition + tool registration
│   ├── config.py            # pydantic-settings (API keys, endpoints)
│   ├── tools/
│   │   ├── strava_tools.py  # 5 Strava tools
│   │   ├── garmin_tools.py  # 5 Garmin tools
│   │   ├── memory_tools.py  # 3 memory tools
│   │   └── running_tools.py # 4 running calculation tools
│   ├── services/
│   │   ├── strava_client.py # Strava API wrapper (stravalib)
│   │   └── garmin_client.py # Garmin API wrapper (python-garminconnect)
│   ├── sessions/
│   │   └── store.py         # Session management (InMemoryMemoryService)
│   └── pyproject.toml       # Python dependencies (uv)
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx
│   │   │   └── DashboardPage.tsx
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   ├── PaceChart.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts   # SSE stream handling
│   │   │   └── useDashboard.ts
│   │   └── api/
│   │       └── client.ts    # Fetch wrapper
│   ├── package.json
│   └── vite.config.ts
└── docs/
    └── superpowers/
        └── specs/           # Design specs (this file)
```

## Key Design Decisions

1. **Tools return dicts, not text** — LLM decides formatting and presentation
2. **Rate-limit guards** on all Strava/Garmin API calls (respect free tier limits)
3. **Tools are idempotent** — safe to retry, no side effects on reads
4. **Tool descriptions written for the LLM** — include when to invoke, what each field means
5. **OAuth tokens per-user** — local JSON storage for MVP (single user)
6. **SSE over WebSocket** — chat streaming is unidirectional; SSE is simpler
7. **Single CoachAgent** — ADK handles tool selection; no multi-agent coordination needed for MVP
8. **Dashboard bypasses LLM** — direct tool calls for performance and determinism

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/sessions` | Create new chat session |
| `POST` | `/api/chat/{session_id}` | Send message, get SSE stream |
| `GET`  | `/api/sessions` | List sessions |
| `GET`  | `/api/dashboard/summary` | Dashboard summary (no LLM) |
| `GET`  | `/api/dashboard/activities` | Activity list with filters |
| `GET`  | `/api/dashboard/health` | Health metrics (HR, sleep, stress) |

## Testing Strategy

- **Running tools** — unit tests (pure Python, deterministic)
- **Strava/Garmin clients** — integration tests with recorded fixtures (no live API calls)
- **Agent tool selection** — integration tests with mocked tool outputs
- **FastAPI routes** — pytest + httpx AsyncClient
- **Frontend** — Vitest + React Testing Library for components, Playwright for e2e
