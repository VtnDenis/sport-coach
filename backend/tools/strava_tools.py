def get_recent_activities(limit: int = 10, *, tool_context) -> dict:
    result = tool_context.call_tool(
        "strava_client",
        "get_recent_activities",
        {"limit": limit},
    )
    return {"activities": result or []}


def get_activity_detail(activity_id: int, *, tool_context) -> dict:
    result = tool_context.call_tool(
        "strava_client",
        "get_activity_detail",
        {"activity_id": activity_id},
    )
    return {"activity": result} if result else {"error": "Activity not found or rate limited"}


def get_athlete_stats(*, tool_context) -> dict:
    result = tool_context.call_tool(
        "strava_client",
        "get_athlete_stats",
        {},
    )
    return {"stats": result} if result else {"error": "Could not retrieve athlete stats"}


def get_training_load(*, tool_context) -> dict:
    result = tool_context.call_tool(
        "strava_client",
        "get_training_load",
        {},
    )
    return result or {"note": "Training load data unavailable"}


def get_segment_efforts(segment_id: int, limit: int = 5, *, tool_context) -> dict:
    result = tool_context.call_tool(
        "strava_client",
        "get_segment_efforts",
        {"segment_id": segment_id, "limit": limit},
    )
    return {"efforts": result or []}
