def remember_fact(key: str, value: str, *, tool_context) -> dict:
    tool_context.state.setdefault("memory", {})[key] = value
    return {"status": "remembered", "key": key}


def recall_information(key: str, *, tool_context) -> dict:
    memory = tool_context.state.get("memory", {})
    if key in memory:
        return {"key": key, "value": memory[key]}
    return {"key": key, "value": None, "note": "No information found for this key"}


def get_user_profile(*, tool_context) -> dict:
    memory = tool_context.state.get("memory", {})
    return {
        "preferences": memory,
        "note": "This is your stored profile. Use remember_fact to update preferences.",
    }
