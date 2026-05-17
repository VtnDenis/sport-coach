# Sport Coach MVP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Priority 1 MVP: a web chatbot that connects to Strava & Garmin, answers natural-language running questions via DeepSeek LLM.

**Architecture:** FastAPI wraps Google ADK CoachAgent with LiteLLM→DeepSeek. Tools call Strava/Garmin APIs. React frontend streams chat via SSE. Memory via ADK InMemorySessionService.

**Tech Stack:** Python 3.11+, FastAPI, Google ADK (git main), LiteLLM, DeepSeek, stravalib, python-garminconnect, React 18, Vite, TypeScript

**Scope:** Priority 1 only (Data sync + basic Q&A). Priority 2-4 deferred to future plans.

---

## File Structure

```
sport-coach/
├── backend/
│   ├── main.py              # FastAPI app, routes, SSE streaming
│   ├── agent.py             # ADK LlmAgent + tool registration
│   ├── config.py            # pydantic-settings
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── strava_tools.py  # 5 Strava tools (factory)
│   │   ├── garmin_tools.py  # 5 Garmin tools (factory)
│   │   ├── memory_tools.py  # 3 memory tools (factory)
│   │   └── running_tools.py # 4 running calculation tools
│   ├── services/
│   │   ├── __init__.py
│   │   ├── strava_client.py # Strava API wrapper
│   │   └── garmin_client.py # Garmin API wrapper
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_running_tools.py
│   │   ├── test_strava_client.py
│   │   ├── test_garmin_client.py
│   │   └── test_main.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.tsx          # React entry point + router
│   │   ├── App.tsx           # Layout shell
│   │   ├── App.css           # Global styles
│   │   ├── pages/
│   │   │   └── ChatPage.tsx
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── hooks/
│   │   │   └── useChat.ts
│   │   └── api/
│   │       └── client.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── .env.example
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/config.py`
- Create: `backend/tools/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `.env.example`

- [ ] **Step 1: Create backend directory structure**

```bash
New-Item -ItemType Directory -Path "backend" -Force
New-Item -ItemType Directory -Path "backend\tools" -Force
New-Item -ItemType Directory -Path "backend\services" -Force
New-Item -ItemType Directory -Path "backend\tests" -Force
```

- [ ] **Step 2: Write pyproject.toml**

```toml
[project]
name = "sport-coach"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sse-starlette>=2.0.0",
    "pydantic-settings>=2.5.0",
    "stravalib>=2.0.0",
    "garminconnect>=0.2.30",
    "litellm>=1.50.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

> Note: ADK is installed separately from git main (see Step 3).

- [ ] **Step 3: Install dependencies + ADK from git main**

```bash
Set-Location -LiteralPath "backend"
pip install -e .
pip install git+https://github.com/google/adk-python.git@main
pip install pytest pytest-asyncio pytest-mock
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Verify:
```bash
python -c "from google.adk.agents import LlmAgent; print('ADK OK')"
python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
python -c "from stravalib import Client; print('stravalib OK')"
python -c "from garminconnect import Garmin; print('Garmin OK')"
```

- [ ] **Step 4: Write config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek/deepseek-chat"

    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_access_token: str = ""
    strava_refresh_token: str = ""

    garmin_email: str = ""
    garmin_password: str = ""

    app_name: str = "sport-coach"
    strava_rate_limit_per_15min: int = 180
    garmin_cache_ttl_seconds: int = 300


settings = Settings()
```

- [ ] **Step 5: Write .env.example**

```
DEEPSEEK_API_KEY=sk-your-key-here

STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_ACCESS_TOKEN=
STRAVA_REFRESH_TOKEN=

GARMIN_EMAIL=
GARMIN_PASSWORD=
```

- [ ] **Step 6: Write empty __init__.py files**

```python
# backend/tools/__init__.py
```

```python
# backend/services/__init__.py
```

```python
# backend/tests/__init__.py
```

- [ ] **Step 7: Verify config loads**

```bash
Set-Location -LiteralPath "backend"
python -c "from config import settings; print(settings.app_name)"
```

Expected: `sport-coach`

- [ ] **Step 8: Commit**

```bash
git add backend/pyproject.toml backend/config.py backend/tools/__init__.py backend/services/__init__.py backend/tests/__init__.py .env.example
git commit -m "chore: backend project scaffolding with config and dependencies"
```

---

### Task 2: Running Tools

**Files:**
- Create: `backend/tools/running_tools.py`
- Create: `backend/tests/test_running_tools.py`

- [ ] **Step 1: Write failing test for calculate_pace**

```python
# backend/tests/test_running_tools.py
from tools.running_tools import calculate_pace, predict_race_time, calculate_splits, training_zones


def test_calculate_pace_10k_50min():
    result = calculate_pace(distance_km=10.0, time_seconds=3000.0)
    assert result["pace_per_km"] == "5:00"
    assert result["speed_kmh"] == 12.0


def test_calculate_pace_half_marathon_2h():
    result = calculate_pace(distance_km=21.0975, time_seconds=7200.0)
    assert result["speed_kmh"] == pytest.approx(10.55, rel=0.01)


def test_predict_race_time_riegel_formula():
    result = predict_race_time(known_distance_km=5.0, known_time_seconds=1500.0, target_distance_km=10.0)
    assert result["predicted_seconds"] == pytest.approx(3122.0, rel=0.01)


def test_predict_race_time_5k_to_marathon():
    result = predict_race_time(known_distance_km=5.0, known_time_seconds=1200.0, target_distance_km=42.195)
    assert result["predicted_seconds"] > 10000


def test_calculate_splits_5k_25min():
    result = calculate_splits(total_distance_km=5.0, total_time_seconds=1500.0)
    assert len(result["splits"]) == 5
    assert result["splits"][0]["split"] == "5:00"
    assert result["splits"][4]["split"] == "25:00"


def test_training_zones():
    result = training_zones(max_hr=190, resting_hr=50)
    assert result["max_hr"] == 190
    assert result["resting_hr"] == 50
    zones = result["zones"]
    assert zones["Zone 1 (Recovery)"]["low"] == 120
    assert zones["Zone 1 (Recovery)"]["high"] == 134
    assert zones["Zone 5 (VO2max)"]["low"] == 176
    assert zones["Zone 5 (VO2max)"]["high"] == 190


def test_training_zones_boundaries_dont_overlap():
    result = training_zones(max_hr=185, resting_hr=55)
    zones = list(result["zones"].values())
    for i in range(len(zones) - 1):
        assert zones[i]["high"] == zones[i + 1]["low"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_running_tools.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 7 tests FAIL with ImportError

- [ ] **Step 3: Write running_tools.py implementation**

```python
# backend/tools/running_tools.py
def calculate_pace(distance_km: float, time_seconds: float) -> dict:
    """Calculate pace and speed from distance and time.

    Args:
        distance_km: Distance in kilometers
        time_seconds: Total time in seconds

    Returns:
        dict with pace_per_km (MM:SS format), pace_seconds (float), speed_kmh (float)
    """
    pace_seconds_per_km = time_seconds / distance_km
    pace_minutes = int(pace_seconds_per_km // 60)
    pace_seconds = int(pace_seconds_per_km % 60)
    return {
        "pace_per_km": f"{pace_minutes}:{pace_seconds:02d}",
        "pace_seconds": round(pace_seconds_per_km, 1),
        "speed_kmh": round(distance_km / (time_seconds / 3600), 2),
    }


def predict_race_time(
    known_distance_km: float, known_time_seconds: float, target_distance_km: float
) -> dict:
    """Predict race time for a target distance using Riegel formula.

    T2 = T1 * (D2/D1)^1.06

    Args:
        known_distance_km: Distance of known race in km
        known_time_seconds: Time of known race in seconds
        target_distance_km: Target race distance in km

    Returns:
        dict with predicted_time (H:MM:SS), predicted_seconds (float)
    """
    predicted_seconds = known_time_seconds * (target_distance_km / known_distance_km) ** 1.06
    hours = int(predicted_seconds // 3600)
    minutes = int((predicted_seconds % 3600) // 60)
    seconds = int(predicted_seconds % 60)
    return {
        "predicted_time": f"{hours}:{minutes:02d}:{seconds:02d}",
        "predicted_seconds": round(predicted_seconds, 1),
    }


def calculate_splits(total_distance_km: float, total_time_seconds: float) -> dict:
    """Calculate cumulative splits per km for even pacing.

    Args:
        total_distance_km: Total race distance in km
        total_time_seconds: Target finish time in seconds

    Returns:
        dict with splits list of {"km": int, "split": "M:SS"}
    """
    pace_per_km = total_time_seconds / total_distance_km
    splits = []
    cumulative = 0.0
    for km in range(1, int(total_distance_km) + 1):
        cumulative += pace_per_km
        mins = int(cumulative // 60)
        secs = int(cumulative % 60)
        splits.append({"km": km, "split": f"{mins}:{secs:02d}"})
    return {"distance_km": total_distance_km, "target_time_seconds": total_time_seconds, "splits": splits}


def training_zones(max_hr: int, resting_hr: int) -> dict:
    """Calculate heart rate training zones using Karvonen (HRR) method.

    Args:
        max_hr: Maximum heart rate in bpm
        resting_hr: Resting heart rate in bpm

    Returns:
        dict with max_hr, resting_hr, zones with low/high bpm per zone
    """
    reserve = max_hr - resting_hr
    zones = {
        "Zone 1 (Recovery)": (0.50, 0.60),
        "Zone 2 (Endurance)": (0.60, 0.70),
        "Zone 3 (Tempo)": (0.70, 0.80),
        "Zone 4 (Threshold)": (0.80, 0.90),
        "Zone 5 (VO2max)": (0.90, 1.00),
    }
    return {
        "max_hr": max_hr,
        "resting_hr": resting_hr,
        "zones": {
            name: {"low": int(resting_hr + low * reserve), "high": int(resting_hr + high * reserve)}
            for name, (low, high) in zones.items()
        },
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_running_tools.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tools/running_tools.py backend/tests/test_running_tools.py
git commit -m "feat: add running calculation tools (pace, race prediction, splits, HR zones)"
```

---

### Task 3: Strava Client Service

**Files:**
- Create: `backend/services/strava_client.py`
- Create: `backend/tests/test_strava_client.py`

- [ ] **Step 1: Write failing test for StravaClient**

```python
# backend/tests/test_strava_client.py
from datetime import datetime, timedelta, timezone

import pytest


class TestStravaClient:
    def test_recent_activities_returns_list_of_dicts(self, mocker):
        mock_activity = mocker.MagicMock()
        mock_activity.model_dump.return_value = {
            "id": 12345,
            "name": "Morning Run",
            "type": "Run",
            "distance": 10000.0,
            "moving_time": 3000.0,
            "start_date": datetime.now(timezone.utc),
        }
        mocker.patch("stravalib.Client")
        from services.strava_client import StravaClient
        from config import settings

        client = StravaClient(settings)
        client._client.get_activities = mocker.MagicMock(return_value=[mock_activity])

        result = client.get_recent_activities(limit=5)

        assert len(result) == 1
        assert result[0]["name"] == "Morning Run"
        assert result[0]["distance"] == 10000.0

    def test_athlete_stats_returns_dict(self, mocker):
        mocker.patch("stravalib.Client")
        mock_stats = mocker.MagicMock()
        mock_stats.model_dump.return_value = {
            "recent_run_totals": {"count": 5, "distance": 50000.0},
            "ytd_run_totals": {"count": 50, "distance": 500000.0},
        }
        from services.strava_client import StravaClient
        from config import settings

        client = StravaClient(settings)
        client._client.get_athlete_stats = mocker.MagicMock(return_value=mock_stats)

        result = client.get_athlete_stats()

        assert result["recent_run_totals"]["count"] == 5
        assert result["ytd_run_totals"]["distance"] == 500000.0

    def test_rate_limiter_prevents_too_many_calls(self, mocker):
        mocker.patch("stravalib.Client")
        from services.strava_client import StravaClient
        from config import settings

        settings.strava_rate_limit_per_15min = 1
        client = StravaClient(settings)
        client._client.get_activities = mocker.MagicMock(return_value=[])

        client.get_recent_activities(limit=5)
        with pytest.raises(RuntimeError, match="Strava rate limit"):
            client.get_recent_activities(limit=5)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_strava_client.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 3 tests FAIL with ModuleNotFoundError

- [ ] **Step 3: Write strava_client.py implementation**

```python
# backend/services/strava_client.py
import time
from datetime import datetime, timezone

from stravalib import Client

from config import Settings


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: int = 900):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._calls: list[float] = []

    def _trim(self):
        now = time.time()
        self._calls = [t for t in self._calls if now - t < self.window_seconds]

    def acquire(self):
        self._trim()
        if len(self._calls) >= self.max_calls:
            raise RuntimeError(f"Strava rate limit reached: {self.max_calls} calls per {self.window_seconds}s")
        self._calls.append(time.time())


class StravaClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = Client()
        self._rate_limiter = RateLimiter(settings.strava_rate_limit_per_15min)

    def _check_auth(self):
        if not self.settings.strava_access_token:
            raise RuntimeError("Strava access token not configured. Set STRAVA_ACCESS_TOKEN in .env")
        self._client.access_token = self.settings.strava_access_token

    def get_recent_activities(self, limit: int = 10) -> list[dict]:
        self._rate_limiter.acquire()
        self._check_auth()
        activities = self._client.get_activities(limit=limit)
        return [a.model_dump() for a in activities]

    def get_activity_detail(self, activity_id: int) -> dict:
        self._rate_limiter.acquire()
        self._check_auth()
        activity = self._client.get_activity(activity_id)
        return activity.model_dump()

    def get_athlete_stats(self) -> dict:
        self._rate_limiter.acquire()
        self._check_auth()
        stats = self._client.get_athlete_stats()
        return stats.model_dump()

    def get_training_load(self) -> dict:
        self._rate_limiter.acquire()
        self._check_auth()
        athlete = self._client.get_athlete()
        stats = self._client.get_athlete_stats()
        return {
            "athlete_id": athlete.id,
            "recent_run_distance": getattr(stats.recent_run_totals, "distance", None),
            "ytd_run_distance": getattr(stats.ytd_run_totals, "distance", None),
        }

    def get_segment_efforts(self, segment_id: int, limit: int = 10) -> list[dict]:
        self._rate_limiter.acquire()
        self._check_auth()
        efforts = self._client.get_segment_efforts(segment_id)
        return [e.model_dump() for e in list(efforts)[:limit]]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_strava_client.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/strava_client.py backend/tests/test_strava_client.py
git commit -m "feat: add Strava API client with rate limiting"
```

---

### Task 4: Garmin Client Service

**Files:**
- Create: `backend/services/garmin_client.py`
- Create: `backend/tests/test_garmin_client.py`

- [ ] **Step 1: Write failing test for GarminClient**

```python
# backend/tests/test_garmin_client.py
from datetime import date

import pytest


class TestGarminClient:
    def test_health_snapshot_returns_dict(self, mocker):
        mocker.patch("garminconnect.Garmin")
        from services.garmin_client import GarminClient
        from config import settings

        client = GarminClient(settings)
        today = date.today().isoformat()
        client._api.get_stats = mocker.MagicMock(return_value={"steps": 10000})
        client._api.get_heart_rates = mocker.MagicMock(return_value={"restingHeartRate": 55})
        client._api.get_all_day_stress = mocker.MagicMock(return_value={"stressValues": []})

        result = client.get_health_snapshot()

        assert "heart_rate" in result
        assert result["heart_rate"]["resting"] == 55
        assert result["steps"] == 10000

    def test_sleep_data_returns_dict(self, mocker):
        mocker.patch("garminconnect.Garmin")
        from services.garmin_client import GarminClient
        from config import settings

        client = GarminClient(settings)
        client._api.get_sleep_data = mocker.MagicMock(return_value={
            "dailySleepDTO": {
                "sleepTimeSeconds": 28800,
                "deepSleepSeconds": 7200,
                "remSleepSeconds": 5400,
            }
        })

        result = client.get_sleep_data()

        assert result["total_sleep_hours"] == 8.0
        assert result["deep_sleep_hours"] == 2.0

    def test_caches_results_within_ttl(self, mocker):
        mocker.patch("garminconnect.Garmin")
        from services.garmin_client import GarminClient
        from config import settings

        settings.garmin_cache_ttl_seconds = 999
        client = GarminClient(settings)
        client._api.get_heart_rates = mocker.MagicMock(return_value={"restingHeartRate": 55})

        client.get_heart_rate()
        client.get_heart_rate()

        assert client._api.get_heart_rates.call_count == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_garmin_client.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 3 tests FAIL with ModuleNotFoundError

- [ ] **Step 3: Write garmin_client.py implementation**

```python
# backend/services/garmin_client.py
import time
from datetime import date, datetime, timedelta

from garminconnect import Garmin

from config import Settings


class GarminClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._api = None
        self._cache: dict[str, tuple[float, dict]] = {}

    def _ensure_connected(self):
        if self._api is not None:
            return
        if not self.settings.garmin_email or not self.settings.garmin_password:
            raise RuntimeError("Garmin credentials not configured. Set GARMIN_EMAIL and GARMIN_PASSWORD in .env")
        self._api = Garmin(
            self.settings.garmin_email,
            self.settings.garmin_password,
            prompt_mfa=lambda: None,
        )
        self._api.login()

    def _cached(self, key: str, fetcher):
        now = time.time()
        if key in self._cache:
            timestamp, value = self._cache[key]
            if now - timestamp < self.settings.garmin_cache_ttl_seconds:
                return value
        result = fetcher()
        self._cache[key] = (now, result)
        return result

    def _today(self) -> str:
        return date.today().isoformat()

    def get_health_snapshot(self) -> dict:
        self._ensure_connected()
        today = self._today()
        stats = self._api.get_stats(today)
        hr = self._api.get_heart_rates(today)
        stress = self._api.get_all_day_stress(today)
        return {
            "date": today,
            "steps": stats.get("totalSteps", 0),
            "calories": stats.get("totalKilocalories", 0),
            "heart_rate": {
                "resting": hr.get("restingHeartRate"),
                "max": hr.get("maxHeartRate"),
            },
            "stress": {
                "values": stress.get("stressValues", []),
            },
        }

    def get_sleep_data(self, days_ago: int = 0) -> dict:
        self._ensure_connected()
        target_date = (date.today() - timedelta(days=days_ago)).isoformat()
        raw = self._api.get_sleep_data(target_date)
        dto = raw.get("dailySleepDTO", {}) if raw else {}
        sleep_seconds = dto.get("sleepTimeSeconds", 0)
        return {
            "date": target_date,
            "total_sleep_hours": round(sleep_seconds / 3600, 1) if sleep_seconds else 0,
            "deep_sleep_hours": round(dto.get("deepSleepSeconds", 0) / 3600, 1),
            "rem_sleep_hours": round(dto.get("remSleepSeconds", 0) / 3600, 1),
            "light_sleep_hours": round(dto.get("lightSleepSeconds", 0) / 3600, 1),
        }

    def get_heart_rate(self) -> dict:
        self._ensure_connected()
        today = self._today()

        def fetch():
            return self._api.get_heart_rates(today)

        hr = self._cached(f"heart_rate_{today}", fetch)
        return {
            "resting_hr": hr.get("restingHeartRate"),
            "max_hr": hr.get("maxHeartRate"),
            "min_hr": hr.get("minHeartRate"),
        }

    def get_training_status(self) -> dict:
        self._ensure_connected()
        today = self._today()
        try:
            status = self._api.get_training_status(today)
        except Exception:
            status = {}
        try:
            readiness = self._api.get_training_readiness(today)
        except Exception:
            readiness = {}
        return {
            "date": today,
            "status": status,
            "readiness": readiness,
        }

    def get_activity_list(self, limit: int = 10) -> list[dict]:
        self._ensure_connected()
        end = date.today()
        start = end - timedelta(days=90)
        activities = self._api.get_activities_by_date(start.isoformat(), end.isoformat())
        result = []
        for a in activities[:limit]:
            result.append({
                "activity_id": a.get("activityId"),
                "name": a.get("activityName"),
                "type": a.get("activityType", {}).get("typeKey"),
                "start_time": a.get("startTimeLocal"),
                "duration_seconds": a.get("duration"),
                "distance_meters": a.get("distance"),
                "avg_hr": a.get("averageHR"),
                "calories": a.get("calories"),
            })
        return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_garmin_client.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/garmin_client.py backend/tests/test_garmin_client.py
git commit -m "feat: add Garmin Connect API client with caching"
```

---

### Task 5: Strava Tools

**Files:**
- Create: `backend/tools/strava_tools.py`

- [ ] **Step 1: Write strava_tools.py (factory function)**

```python
# backend/tools/strava_tools.py
from services.strava_client import StravaClient


def create_strava_tools(client: StravaClient) -> list:
    def get_recent_activities(limit: int = 10) -> dict:
        """Get the user's most recent Strava activities.

        Use this when the user asks about their recent runs, workouts, or training history.
        Returns activity name, type, distance, moving time, pace, elevation, and start date.

        Args:
            limit: Number of recent activities to return (default 10, max 30)
        """
        activities = client.get_recent_activities(limit=min(limit, 30))
        return {
            "count": len(activities),
            "activities": [
                {
                    "name": a.get("name"),
                    "type": a.get("type"),
                    "distance_meters": a.get("distance"),
                    "moving_time_seconds": a.get("moving_time"),
                    "elapsed_time_seconds": a.get("elapsed_time"),
                    "elevation_gain_meters": a.get("total_elevation_gain"),
                    "start_date": str(a.get("start_date")),
                    "average_speed": a.get("average_speed"),
                    "id": a.get("id"),
                }
                for a in activities
            ],
        }

    def get_activity_detail(activity_id: int) -> dict:
        """Get full details for a specific Strava activity.

        Use this when the user asks about a specific run or workout in detail.
        Returns complete data including splits, heart rate, map, laps, and segment efforts.

        Args:
            activity_id: The Strava activity ID
        """
        a = client.get_activity_detail(activity_id)
        return {
            "id": a.get("id"),
            "name": a.get("name"),
            "type": a.get("type"),
            "distance_meters": a.get("distance"),
            "moving_time_seconds": a.get("moving_time"),
            "elapsed_time_seconds": a.get("elapsed_time"),
            "elevation_gain_meters": a.get("total_elevation_gain"),
            "start_date": str(a.get("start_date")),
            "average_speed": a.get("average_speed"),
            "max_speed": a.get("max_speed"),
            "average_heartrate": a.get("average_heartrate"),
            "max_heartrate": a.get("max_heartrate"),
            "description": a.get("description"),
            "calories": a.get("calories"),
        }

    def get_athlete_stats() -> dict:
        """Get the athlete's overall statistics from Strava.

        Use this when the user asks about their overall progress, yearly totals,
        personal records, or training volume over time.
        Returns all-time, YTD, and recent (4-week) totals for runs, rides, and swims.
        """
        stats = client.get_athlete_stats()
        return stats

    def get_training_load() -> dict:
        """Get the athlete's recent training load from Strava.

        Use this when the user asks about their training load, fitness, fatigue, or form.
        Returns recent and year-to-date run distances.
        """
        return client.get_training_load()

    def get_segment_efforts(segment_id: int = 0, limit: int = 10) -> dict:
        """Get segment efforts from Strava.

        Use this when the user asks about their performance on specific segments
        or wants to see leaderboard results.

        Args:
            segment_id: The Strava segment ID
            limit: Number of efforts to return (default 10)
        """
        if segment_id == 0:
            return {"error": "segment_id is required"}
        efforts = client.get_segment_efforts(segment_id, limit)
        return {"segment_id": segment_id, "efforts": efforts}

    return [
        get_recent_activities,
        get_activity_detail,
        get_athlete_stats,
        get_training_load,
        get_segment_efforts,
    ]
```

- [ ] **Step 2: Commit**

```bash
git add backend/tools/strava_tools.py
git commit -m "feat: add Strava tool functions wrapping strava client"
```

---

### Task 6: Garmin Tools

**Files:**
- Create: `backend/tools/garmin_tools.py`

- [ ] **Step 1: Write garmin_tools.py (factory function)**

```python
# backend/tools/garmin_tools.py
from services.garmin_client import GarminClient


def create_garmin_tools(client: GarminClient) -> list:
    def get_health_snapshot() -> dict:
        """Get today's health snapshot from Garmin Connect.

        Use this when the user asks about their current health status, daily activity,
        steps, heart rate, stress, or body battery.
        Returns steps, calories, resting/max heart rate, and stress levels.
        """
        return client.get_health_snapshot()

    def get_sleep_data(days_ago: int = 0) -> dict:
        """Get sleep data from Garmin Connect.

        Use this when the user asks about their sleep quality, duration, sleep stages,
        or recovery.
        Returns total sleep, deep sleep, REM sleep, and light sleep in hours.

        Args:
            days_ago: How many days back to look (0 = last night, 1 = night before, etc.)
        """
        return client.get_sleep_data(days_ago)

    def get_heart_rate() -> dict:
        """Get heart rate data from Garmin Connect.

        Use this when the user asks about their heart rate, resting HR, or max HR.
        Returns resting, max, and minimum heart rate for today.
        """
        return client.get_heart_rate()

    def get_training_status() -> dict:
        """Get training status and readiness from Garmin Connect.

        Use this when the user asks about their training status, recovery state,
        VO2max, training load, or whether they should train today.
        Returns training status, load, VO2max, and recovery metrics.
        """
        return client.get_training_status()

    def get_activity_list(limit: int = 10) -> dict:
        """Get recent activity list from Garmin Connect.

        Use this when the user asks about their activity history or recent workouts
        recorded on their Garmin device.
        Returns activity name, type, duration, distance, average HR, and calories.

        Args:
            limit: Number of activities to return (default 10, max 20)
        """
        activities = client.get_activity_list(limit=min(limit, 20))
        return {"count": len(activities), "activities": activities}

    return [
        get_health_snapshot,
        get_sleep_data,
        get_heart_rate,
        get_training_status,
        get_activity_list,
    ]
```

- [ ] **Step 2: Commit**

```bash
git add backend/tools/garmin_tools.py
git commit -m "feat: add Garmin tool functions wrapping garmin client"
```

---

### Task 7: Memory Tools

**Files:**
- Create: `backend/tools/memory_tools.py`

- [ ] **Step 1: Write memory_tools.py**

```python
# backend/tools/memory_tools.py
from google.adk.tools import ToolContext


def remember_fact(key: str, value: str, tool_context: ToolContext) -> dict:
    """Store a fact in the user's memory for future reference.

    Use this to remember user preferences, personal records, goals, injuries,
    or any information the user explicitly shares that should be recalled later.

    Args:
        key: Short label for the fact (e.g. "goal_5k_time", "injury_left_knee")
        value: The information to remember
    """
    tool_context.state[key] = value
    return {"status": "stored", "key": key}


def recall_information(query: str, tool_context: ToolContext) -> dict:
    """Search the user's memory for relevant stored information.

    Use this when the user asks about something they've previously shared
    (preferences, goals, injury history, personal records).
    Searches all stored facts by matching the query against keys and values.

    Args:
        query: What to search for in memory
    """
    results = {}
    for k, v in tool_context.state.items():
        if query.lower() in k.lower() or query.lower() in str(v).lower():
            results[k] = v
    return {"query": query, "results": results, "found": len(results)}


def get_user_profile(tool_context: ToolContext) -> dict:
    """Get the complete user profile stored in memory.

    Use this at the start of a conversation to understand the user's background:
    goals, preferences, injury history, personal records, and equipment.
    """
    keys_of_interest = [
        "goal_5k_time", "goal_10k_time", "goal_half_marathon_time",
        "goal_marathon_time", "preferred_unit", "injury_history",
        "weekly_mileage_goal", "shoe_model", "shoe_mileage",
    ]
    profile = {}
    for key in keys_of_interest:
        if key in tool_context.state:
            profile[key] = tool_context.state[key]
    return {"profile": profile, "total_facts": len(tool_context.state)}
```

- [ ] **Step 2: Commit**

```bash
git add backend/tools/memory_tools.py
git commit -m "feat: add memory tools (remember, recall, user profile)"
```

---

### Task 8: CoachAgent

**Files:**
- Create: `backend/agent.py`

- [ ] **Step 1: Write agent.py**

```python
# backend/agent.py
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from config import settings
from services.garmin_client import GarminClient
from services.strava_client import StravaClient
from tools.garmin_tools import create_garmin_tools
from tools.memory_tools import get_user_profile, recall_information, remember_fact
from tools.running_tools import calculate_pace, calculate_splits, predict_race_time, training_zones
from tools.strava_tools import create_strava_tools

COACH_INSTRUCTION = """You are a knowledgeable running coach assistant. You help runners improve their performance,
understand their data, and make informed training decisions.

## Your capabilities:
- Access the user's Strava activities to analyze runs, pace, distance, and trends
- Access Garmin Connect health data (heart rate, sleep, stress, training status)
- Remember user preferences, goals, and personal records for personalized advice
- Perform running calculations (pace, race predictions, splits, HR training zones)

## How to respond:
- Be encouraging and supportive, like a real coach
- When analyzing data, explain what the numbers mean in practical terms
- Use the tools available to you before answering — don't guess at data
- If a question requires data you don't have access to, explain what's needed
- Provide specific, actionable advice based on the data
- Format your responses clearly with bullet points for lists of recommendations
- When sharing pace or time data, express it in MM:SS format per km

## Important:
- Always check memory first to recall user preferences and goals
- If the user shares a personal record, goal, or preference, remember it
- Use Strava for activity/performance questions, Garmin for health/recovery questions
- When discussing training intensity, reference heart rate zones
"""


def create_agent() -> LlmAgent:
    strava_client = StravaClient(settings)
    garmin_client = GarminClient(settings)

    all_tools = (
        create_strava_tools(strava_client)
        + create_garmin_tools(garmin_client)
        + [remember_fact, recall_information, get_user_profile]
        + [calculate_pace, predict_race_time, calculate_splits, training_zones]
    )

    return LlmAgent(
        model=LiteLlm(model=settings.deepseek_model),
        name="CoachAgent",
        description="A running coach that analyzes Strava and Garmin data to provide personalized advice.",
        instruction=COACH_INSTRUCTION,
        tools=all_tools,
    )
```

- [ ] **Step 2: Verify agent creation works**

```bash
Set-Location -LiteralPath "backend"
python -c "from agent import create_agent; agent = create_agent(); print(f'Agent created: {agent.name}'); print(f'Tools: {len(agent.tools)}')"
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: `Agent created: CoachAgent` with 17 tools

- [ ] **Step 3: Commit**

```bash
git add backend/agent.py
git commit -m "feat: add CoachAgent with all tools and LiteLLM/DeepSeek model"
```

---

### Task 9: FastAPI App (Sessions + Chat SSE)

**Files:**
- Create: `backend/main.py`
- Create: `backend/tests/test_main.py`

- [ ] **Step 1: Write failing tests for API routes**

```python
# backend/tests/test_main.py
import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_session(client):
    response = await client.post("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"].startswith("sess_")


@pytest.mark.asyncio
async def test_list_sessions(client):
    await client.post("/api/sessions")
    response = await client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["sessions"], list)


@pytest.mark.asyncio
async def test_chat_requires_valid_session(client):
    response = await client.post("/api/chat/nonexistent", json={"message": "hello"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_main.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 4 tests FAIL with ModuleNotFoundError

- [ ] **Step 3: Write main.py**

```python
# backend/main.py
import json
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent import create_agent
from config import settings

app = FastAPI(title="Sport Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
agent = create_agent()
runner = Runner(agent=agent, app_name=settings.app_name, session_service=session_service)


class ChatRequest(BaseModel):
    message: str


@app.post("/api/sessions")
async def create_session():
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    await session_service.create_session(
        app_name=settings.app_name,
        user_id="default",
        session_id=session_id,
    )
    return {"session_id": session_id}


@app.get("/api/sessions")
async def list_sessions():
    sessions = await session_service.list_sessions(
        app_name=settings.app_name,
        user_id="default",
    )
    return {"sessions": [{"id": s.id} for s in sessions]}


@app.post("/api/chat/{session_id}")
async def chat(session_id: str, request: ChatRequest):
    try:
        await session_service.get_session(
            app_name=settings.app_name,
            user_id="default",
            session_id=session_id,
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found") from None

    async def event_stream():
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)],
        )
        async for event in runner.run_async(
            user_id="default",
            session_id=session_id,
            new_message=user_content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    text = event.content.parts[0].text or ""
                    yield {"event": "message", "data": text}
            elif event.content and event.content.parts:
                text = event.content.parts[0].text or ""
                if text:
                    yield {"event": "message", "data": text}

        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(event_stream())


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/dashboard/summary")
async def dashboard_summary():
    return {
        "message": "Dashboard coming in Priority 2. Chat is available at /api/chat/{session_id}",
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
Set-Location -LiteralPath "backend"
pytest tests/test_main.py -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/main.py backend/tests/test_main.py
git commit -m "feat: add FastAPI app with session management and SSE chat streaming"
```

---

### Task 10: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`

- [ ] **Step 1: Create frontend directory and write package.json**

```bash
New-Item -ItemType Directory -Path "frontend\src\pages" -Force
New-Item -ItemType Directory -Path "frontend\src\components" -Force
New-Item -ItemType Directory -Path "frontend\src\hooks" -Force
New-Item -ItemType Directory -Path "frontend\src\api" -Force
```

```json
// frontend/package.json
{
  "name": "sport-coach-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "typescript": "~5.6.2",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 2: Write tsconfig.json**

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Write vite.config.ts**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Write index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sport Coach</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏃</text></svg>" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Install frontend dependencies**

```bash
Set-Location -LiteralPath "frontend"
npm install
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/tsconfig.json frontend/vite.config.ts frontend/index.html frontend/package-lock.json
git commit -m "chore: scaffold React + Vite + TypeScript frontend"
```

---

### Task 11: API Client

**Files:**
- Create: `frontend/src/api/client.ts`

- [ ] **Step 1: Write api/client.ts**

```typescript
// frontend/src/api/client.ts
const BASE_URL = '/api'

export async function createSession(): Promise<string> {
  const res = await fetch(`${BASE_URL}/sessions`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to create session: ${res.status}`)
  const data = await res.json()
  return data.session_id
}

export async function listSessions(): Promise<{ id: string }[]> {
  const res = await fetch(`${BASE_URL}/sessions`)
  if (!res.ok) throw new Error(`Failed to list sessions: ${res.status}`)
  const data = await res.json()
  return data.sessions
}

export function streamChat(
  sessionId: string,
  message: string,
  onMessage: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): AbortController {
  const controller = new AbortController()

  fetch(`${BASE_URL}/chat/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Chat error: ${response.status}`)
      }
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const parsed = JSON.parse(line.slice(6))
              if (parsed.event === 'message' && parsed.data) {
                onMessage(parsed.data)
              } else if (parsed.event === 'done') {
                onDone()
              }
            } catch {
              // skip malformed lines
            }
          }
        }
      }
      onDone()
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError(err)
      }
    })

  return controller
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/client.ts
git commit -m "feat: add API client for sessions and SSE chat streaming"
```

---

### Task 12: useChat Hook

**Files:**
- Create: `frontend/src/hooks/useChat.ts`

- [ ] **Step 1: Write hooks/useChat.ts**

```typescript
// frontend/src/hooks/useChat.ts
import { useCallback, useRef, useState } from 'react'
import { createSession, streamChat } from '../api/client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const assistantIdRef = useRef<string>('')

  const newSession = useCallback(async () => {
    abortRef.current?.abort()
    const sid = await createSession()
    setSessionId(sid)
    setMessages([])
    setIsStreaming(false)
  }, [])

  const sendMessage = useCallback(
    async (text: string) => {
      if (!sessionId || !text.trim() || isStreaming) return

      const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
      const assistantId = crypto.randomUUID()
      assistantIdRef.current = assistantId
      setMessages((prev) => [...prev, userMsg])
      setIsStreaming(true)

      let content = ''
      setMessages((prev) => [...prev, { id: assistantId, role: 'assistant', content: '' }])

      abortRef.current = streamChat(
        sessionId,
        text,
        (chunk) => {
          content += chunk
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content } : m)),
          )
        },
        () => {
          setIsStreaming(false)
        },
        (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: `Error: ${err.message}` }
                : m,
            ),
          )
          setIsStreaming(false)
        },
      )
    },
    [sessionId, isStreaming],
  )

  return { messages, isStreaming, sessionId, newSession, sendMessage }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/useChat.ts
git commit -m "feat: add useChat hook for SSE streaming and session management"
```

---

### Task 13: Chat Components

**Files:**
- Create: `frontend/src/components/ChatMessage.tsx`
- Create: `frontend/src/components/ChatInput.tsx`

- [ ] **Step 1: Write ChatMessage.tsx**

```tsx
// frontend/src/components/ChatMessage.tsx
interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
}

export function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === 'user'
  return (
    <div className={`message ${isUser ? 'message--user' : 'message--assistant'}`}>
      <div className="message__avatar">
        {isUser ? '🏃' : '🎯'}
      </div>
      <div className="message__content">
        <div className="message__role">{isUser ? 'You' : 'Coach'}</div>
        <div className="message__text">{content || (isUser ? '' : '...')}</div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write ChatInput.tsx**

```tsx
// frontend/src/components/ChatInput.tsx
import { useState, type FormEvent } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim() || disabled) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask your coach anything..."
        disabled={disabled}
        className="chat-input__field"
      />
      <button type="submit" disabled={disabled || !input.trim()} className="chat-input__send">
        Send
      </button>
    </form>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatMessage.tsx frontend/src/components/ChatInput.tsx
git commit -m "feat: add ChatMessage and ChatInput components"
```

---

### Task 14: ChatPage + App Shell

**Files:**
- Create: `frontend/src/pages/ChatPage.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.css`
- Create: `frontend/src/main.tsx`

- [ ] **Step 1: Write ChatPage.tsx**

```tsx
// frontend/src/pages/ChatPage.tsx
import { useEffect, useRef } from 'react'
import { ChatMessage } from '../components/ChatMessage'
import { ChatInput } from '../components/ChatInput'
import { useChat } from '../hooks/useChat'

export function ChatPage() {
  const { messages, isStreaming, sessionId, newSession, sendMessage } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!sessionId) {
      newSession()
    }
  }, [sessionId, newSession])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="chat-page">
      <div className="chat-page__header">
        <h1>Coach Chat</h1>
        <button onClick={newSession} className="chat-page__new-btn">
          + New Chat
        </button>
      </div>
      <div className="chat-page__messages">
        {messages.length === 0 && (
          <div className="chat-page__welcome">
            <h2>Welcome to Sport Coach</h2>
            <p>
              I can analyze your Strava activities and Garmin health data to give
              you personalized running advice. Ask me about:
            </p>
            <ul>
              <li>Your recent runs and performance</li>
              <li>Pace calculations and race predictions</li>
              <li>Heart rate zones and training intensity</li>
              <li>Sleep, recovery, and training readiness</li>
            </ul>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
        ))}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  )
}
```

- [ ] **Step 2: Write Sidebar.tsx**

```tsx
// frontend/src/components/Sidebar.tsx
import { NavLink } from 'react-router-dom'

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__logo">🏃</span>
        <span className="sidebar__title">Sport Coach</span>
      </div>
      <nav className="sidebar__nav">
        <NavLink to="/" className={({ isActive }) => `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}>
          💬 Chat
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}>
          📊 Dashboard
        </NavLink>
      </nav>
      <div className="sidebar__footer">
        <span className="sidebar__status" title="Connected to Strava & Garmin">🟢 Connected</span>
      </div>
    </aside>
  )
}
```

- [ ] **Step 3: Write App.tsx**

```tsx
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { ChatPage } from './pages/ChatPage'
import './App.css'

function DashboardPage() {
  return (
    <div className="page-placeholder">
      <h1>Dashboard</h1>
      <p>Coming in the next update. Chat is ready now!</p>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="app__main">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
```

- [ ] **Step 4: Write App.css**

```css
/* frontend/src/App.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #1a1a1a;
}

.app {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 240px;
  background: #1a1a2e;
  color: #e0e0e0;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  flex-shrink: 0;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #2a2a4e;
  margin-bottom: 1rem;
}

.sidebar__logo { font-size: 1.5rem; }
.sidebar__title { font-size: 1.1rem; font-weight: 700; }

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.sidebar__link {
  color: #a0a0c0;
  text-decoration: none;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: background 0.15s;
}

.sidebar__link:hover { background: #2a2a4e; }
.sidebar__link--active {
  background: #3a3a6e;
  color: #fff;
  font-weight: 600;
}

.sidebar__footer { padding-top: 1rem; border-top: 1px solid #2a2a4e; font-size: 0.8rem; }

.app__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-page__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
}

.chat-page__header h1 { font-size: 1.2rem; }

.chat-page__new-btn {
  background: #3a3a6e;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.chat-page__new-btn:hover { background: #4a4a8e; }

.chat-page__messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-page__welcome {
  text-align: center;
  margin-top: 3rem;
  color: #666;
}

.chat-page__welcome h2 { font-size: 1.3rem; margin-bottom: 0.5rem; color: #333; }
.chat-page__welcome ul { text-align: left; display: inline-block; margin-top: 0.5rem; }
.chat-page__welcome li { margin-bottom: 0.25rem; }

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.message--user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message__avatar { font-size: 1.5rem; flex-shrink: 0; }
.message__role { font-size: 0.75rem; color: #888; margin-bottom: 0.25rem; }

.message__content {
  background: #fff;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.message--user .message__content {
  background: #3a3a6e;
  color: #fff;
}

.message--user .message__role { color: #c0c0e0; }

.message__text {
  font-size: 0.95rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.chat-input {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: #fff;
  border-top: 1px solid #e0e0e0;
}

.chat-input__field {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
}

.chat-input__field:focus { border-color: #3a3a6e; }

.chat-input__send {
  background: #3a3a6e;
  color: #fff;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
}

.chat-input__send:disabled {
  background: #c0c0c0;
  cursor: default;
}

.page-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
}

.page-placeholder h1 { font-size: 1.5rem; margin-bottom: 0.5rem; color: #555; }
```

- [ ] **Step 5: Write main.tsx**

```tsx
// frontend/src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 6: Verify frontend builds**

```bash
Set-Location -LiteralPath "frontend"
npm run build
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: Build succeeds with no errors

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add ChatPage, Sidebar, App shell with CSS"
```

---

### Task 15: Integration Verification

- [ ] **Step 1: Start backend and verify it runs**

```bash
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "backend"
Start-Sleep -Seconds 3
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

Expected: `{"status":"ok"}`

- [ ] **Step 2: Verify session creation works**

```bash
$body = Invoke-WebRequest -Uri "http://localhost:8000/api/sessions" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
Write-Host $body
```

Expected: JSON with `session_id` starting with `sess_`

- [ ] **Step 3: Verify frontend dev server starts**

```bash
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend"
Start-Sleep -Seconds 3
Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5 | Select-Object StatusCode
```

Expected: 200

- [ ] **Step 4: Stop servers and commit (if changes)**

```bash
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
```

No commit needed unless issues were fixed during verification.

---

### Task 16: Run Full Test Suite

- [ ] **Step 1: Run all backend tests**

```bash
Set-Location -LiteralPath "backend"
pytest tests/ -v
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: All tests PASS (10+ tests from running_tools, strava_client, garmin_client, main)

- [ ] **Step 2: Verify frontend TypeScript compiles**

```bash
Set-Location -LiteralPath "frontend"
npx tsc --noEmit
Remove-Variable pwd -ErrorAction SilentlyContinue; Set-Location -LiteralPath "C:\Users\vtnde\Documents\Projets\sport-coach"
```

Expected: No TypeScript errors

---

## Next Steps After MVP

Priority 2 (Dashboard): Add recharts, `useDashboard` hook, `DashboardPage`, `StatsCard`, `PaceChart` components, and real data in `/api/dashboard/*` routes.

Priority 3 (Proactive coaching): Scheduled background analysis, push notifications, weekly summaries.

Priority 4 (Training plans): Plan generation, calendar integration, progress tracking.
