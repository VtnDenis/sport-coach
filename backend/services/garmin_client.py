import json
import os
import time

from garminconnect import Garmin

from backend.config import settings

TOKEN_PATH = os.path.expanduser("~/.garminconnect/garmin_tokens.json")


class GarminClient:
    def __init__(self):
        self._client: Garmin | None = None
        self._last_request_time: float = 0.0

    @property
    def client(self) -> Garmin:
        if self._client is None:
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            try:
                self._client = Garmin(
                    email=settings.garmin_email,
                    password=settings.garmin_password,
                )
                self._client.login()
            except Exception:
                self._client = Garmin()
            self._save_tokens()
        return self._client

    def _save_tokens(self):
        try:
            tokens = self._client.garth.dumps()
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as f:
                json.dump(tokens, f, indent=2)
        except Exception:
            pass

    def _respect_rate_limit(self):
        now = time.monotonic()
        elapsed = now - self._last_request_time
        min_interval = 0.5
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.monotonic()

    def get_health_snapshot(self, date_str: str | None = None) -> dict | None:
        self._respect_rate_limit()
        try:
            if date_str:
                data = self.client.get_health_data(date_str)
            else:
                data = self.client.get_health_data()
        except Exception:
            return None
        return self._parse_health(data)

    def _parse_health(self, data: dict) -> dict:
        return {
            "resting_heart_rate": data.get("restingHeartRate"),
            "max_heart_rate": data.get("maxHeartRate"),
            "average_stress": data.get("averageStressLevel"),
            "body_battery": {
                "charged": data.get("bodyBatteryChargedValue"),
                "drained": data.get("bodyBatteryDrainedValue"),
                "highest": data.get("bodyBatteryHighestValue"),
                "lowest": data.get("bodyBatteryLowestValue"),
            },
            "floors_climbed": data.get("floorsClimbed"),
            "average_respiration": data.get("averageRespiration"),
        }

    def get_sleep_data(self, date_str: str | None = None) -> dict | None:
        self._respect_rate_limit()
        try:
            if date_str:
                data = self.client.get_sleep_data(date_str)
            else:
                data = self.client.get_sleep_data()
        except Exception:
            return None
        return {
            "sleep_score": data.get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value"),
            "sleep_time_seconds": data.get("dailySleepDTO", {}).get("sleepTimeSeconds"),
            "awake_time_seconds": data.get("dailySleepDTO", {}).get("awakeSleepSeconds"),
            "deep_sleep_seconds": data.get("dailySleepDTO", {}).get("deepSleepSeconds"),
            "light_sleep_seconds": data.get("dailySleepDTO", {}).get("lightSleepSeconds"),
            "rem_sleep_seconds": data.get("dailySleepDTO", {}).get("remSleepSeconds"),
        }

    def get_heart_rate(self, date_str: str | None = None) -> dict | None:
        self._respect_rate_limit()
        try:
            if date_str:
                data = self.client.get_heart_rates(date_str)
            else:
                data = self.client.get_heart_rates()
        except Exception:
            return None
        vals = data.get("heartRateValues", [])
        if not vals:
            return {"resting_hr": None, "max_hr": None, "min_hr": None, "hr_readings": []}
        hr_values = [v[1] for v in vals if v]
        return {
            "resting_hr": data.get("restingHeartRate"),
            "max_hr": max(hr_values) if hr_values else None,
            "min_hr": min(hr_values) if hr_values else None,
            "hr_readings": vals[:100],
            "off_wrist": data.get("offWrist"),
        }

    def get_training_status(self) -> dict | None:
        self._respect_rate_limit()
        try:
            status = self.client.get_training_status()
        except Exception:
            return None
        return {
            "training_status": status.get("trainingStatus"),
            "vo2max": status.get("vo2Max"),
            "ftp": status.get("functionalThresholdPower"),
            "load_focus": status.get("loadFocus", {}),
        }

    def get_activity_list(self, limit: int = 10) -> list[dict]:
        self._respect_rate_limit()
        try:
            activities = self.client.get_activities(0, limit)
        except Exception:
            return []
        return [
            {
                "activity_id": a.get("activityId"),
                "name": a.get("activityName"),
                "type": a.get("activityType", {}).get("typeKey"),
                "start_time": a.get("startTimeLocal"),
                "distance_m": a.get("distance"),
                "duration_s": a.get("duration"),
                "calories": a.get("calories"),
                "avg_hr": a.get("averageHR"),
                "max_hr": a.get("maxHR"),
            }
            for a in activities
        ]
