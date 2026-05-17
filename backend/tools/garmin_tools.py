def get_health_snapshot(date_str: str | None = None, *, tool_context) -> dict:
    kwargs = {}
    if date_str:
        kwargs["date_str"] = date_str
    result = tool_context.call_tool("garmin_client", "get_health_snapshot", kwargs)
    return result if result else {"error": "Could not retrieve health snapshot"}


def get_sleep_data(date_str: str | None = None, *, tool_context) -> dict:
    kwargs = {}
    if date_str:
        kwargs["date_str"] = date_str
    result = tool_context.call_tool("garmin_client", "get_sleep_data", kwargs)
    return result if result else {"error": "Could not retrieve sleep data"}


def get_heart_rate(date_str: str | None = None, *, tool_context) -> dict:
    kwargs = {}
    if date_str:
        kwargs["date_str"] = date_str
    result = tool_context.call_tool("garmin_client", "get_heart_rate", kwargs)
    return result if result else {"error": "Could not retrieve heart rate data"}


def get_training_status(*, tool_context) -> dict:
    result = tool_context.call_tool("garmin_client", "get_training_status", {})
    return result if result else {"error": "Could not retrieve training status"}


def get_activity_list(limit: int = 10, *, tool_context) -> dict:
    result = tool_context.call_tool("garmin_client", "get_activity_list", {"limit": limit})
    return {"activities": result or []}
