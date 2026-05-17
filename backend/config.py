from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    deepseek_api_key: str = ""
    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_access_token: str = ""
    strava_refresh_token: str = ""
    garmin_email: str = ""
    garmin_password: str = ""

    @property
    def deepseek_configured(self) -> bool:
        return bool(self.deepseek_api_key)

    @property
    def strava_configured(self) -> bool:
        return bool(self.strava_client_id and self.strava_client_secret)

    @property
    def garmin_configured(self) -> bool:
        return bool(self.garmin_email and self.garmin_password)


settings = Settings()
