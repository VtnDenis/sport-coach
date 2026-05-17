import time

from stravalib.client import Client
from stravalib.exc import RateLimitExceeded

from backend.config import settings


class StravaClient:
    def __init__(self):
        self._client: Client | None = None
        self._last_request_time: float = 0.0

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client()
            if settings.strava_access_token:
                self._client.access_token = settings.strava_access_token
        return self._client

    def _respect_rate_limit(self):
        now = time.monotonic()
        elapsed = now - self._last_request_time
        min_interval = 0.3
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.monotonic()

    def get_recent_activities(self, limit: int = 10) -> list[dict]:
        self._respect_rate_limit()
        try:
            activities = list(self.client.get_activities(limit=limit))
        except RateLimitExceeded:
            return []
        return [
            {
                "id": a.id,
                "name": a.name,
                "type": str(a.type) if a.type else None,
                "start_date": str(a.start_date_local) if a.start_date_local else None,
                "distance_m": round(a.distance.num, 0) if a.distance else None,
                "moving_time_s": a.moving_time.total_seconds() if a.moving_time else None,
                "elapsed_time_s": a.elapsed_time.total_seconds() if a.elapsed_time else None,
                "total_elevation_gain_m": (
                    round(a.total_elevation_gain.num, 1) if a.total_elevation_gain else None
                ),
                "average_speed_ms": round(a.average_speed.num, 2) if a.average_speed else None,
                "max_speed_ms": round(a.max_speed.num, 2) if a.max_speed else None,
                "average_heartrate": round(a.average_heartrate, 1) if a.average_heartrate else None,
                "max_heartrate": a.max_heartrate,
                "suffer_score": a.suffer_score,
                "kudos_count": a.kudos_count,
            }
            for a in activities
        ]

    def get_activity_detail(self, activity_id: int) -> dict | None:
        self._respect_rate_limit()
        from stravalib.exc import RateLimitExceeded

        try:
            a = self.client.get_activity(activity_id)
        except (RateLimitExceeded, Exception):
            return None
        return {
            "id": a.id,
            "name": a.name,
            "type": str(a.type) if a.type else None,
            "start_date": str(a.start_date_local) if a.start_date_local else None,
            "distance_m": round(a.distance.num, 0) if a.distance else None,
            "moving_time_s": a.moving_time.total_seconds() if a.moving_time else None,
            "elapsed_time_s": a.elapsed_time.total_seconds() if a.elapsed_time else None,
            "total_elevation_gain_m": (
                round(a.total_elevation_gain.num, 1) if a.total_elevation_gain else None
            ),
            "average_speed_ms": round(a.average_speed.num, 2) if a.average_speed else None,
            "max_speed_ms": round(a.max_speed.num, 2) if a.max_speed else None,
            "average_heartrate": round(a.average_heartrate, 1) if a.average_heartrate else None,
            "max_heartrate": a.max_heartrate,
            "suffer_score": a.suffer_score,
            "splits_standard": [
                {
                    "split_num": s.split,
                    "distance_m": round(s.distance.num, 0) if s.distance else None,
                    "elapsed_time_s": s.elapsed_time.total_seconds() if s.elapsed_time else None,
                }
                for s in (a.splits_standard or [])
            ],
        }

    def get_athlete_stats(self, athlete_id: int | None = None) -> dict | None:
        self._respect_rate_limit()
        try:
            stats = self.client.get_athlete_stats(athlete_id)
        except Exception:
            return None
        return {
            "recent_run_totals": {
                "count": stats.recent_run_totals.count,
                "distance_m": round(stats.recent_run_totals.distance.num, 0) if stats.recent_run_totals.distance else None,
                "moving_time_s": stats.recent_run_totals.moving_time.total_seconds() if stats.recent_run_totals.moving_time else None,
            },
            "ytd_run_totals": {
                "count": stats.ytd_run_totals.count,
                "distance_m": round(stats.ytd_run_totals.distance.num, 0) if stats.ytd_run_totals.distance else None,
                "moving_time_s": stats.ytd_run_totals.moving_time.total_seconds() if stats.ytd_run_totals.moving_time else None,
            },
        }

    def get_training_load(self) -> dict | None:
        self._respect_rate_limit()
        return {"note": "Training load data is not available via stravalib free methods. Use athlete stats instead."}

    def get_segment_efforts(self, segment_id: int, limit: int = 5) -> list[dict]:
        self._respect_rate_limit()
        try:
            efforts = list(
                self.client.get_segment_efforts(segment_id, per_page=limit)
            )
        except Exception:
            return []
        return [
            {
                "id": e.id,
                "name": e.name,
                "elapsed_time_s": e.elapsed_time.total_seconds() if e.elapsed_time else None,
                "pr_rank": e.pr_rank,
            }
            for e in efforts
        ]
