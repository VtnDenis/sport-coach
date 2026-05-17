from google.adk.agents import Agent
from google.adk.tools import ToolContext

from backend.config import settings
from backend.tools import strava_tools, garmin_tools, memory_tools, running_tools


COACH_INSTRUCTION = """You are a running coach chatbot named Sport Coach. You help runners improve by analyzing their data from Strava and Garmin and giving personalized advice.

**Your capabilities:**
- Retrieve recent activities, athlete stats, and training load from Strava
- Get health snapshots (heart rate, stress, body battery), sleep data, and training status from Garmin
- Calculate paces, predict race times, generate splits, and determine training zones
- Remember user preferences and recall past information

**How you work:**
1. When the user asks a question, determine which tools you need
2. Invoke the appropriate tools to get data
3. Analyze the data and give a natural, helpful response
4. If the user shares a preference or goal, use remember_fact to store it

**Guidelines:**
- Be encouraging and supportive
- Base all advice on actual data when available
- When data is missing, ask what they'd like to know
- Use metric units (km, meters) by default
- Keep responses concise but informative
- If Strava or Garmin data can't be retrieved (unconfigured, rate limited), tell the user and suggest what they can do

**Important: Always use tools to get real data. Never make up numbers.**
"""


def create_coach_agent() -> Agent:
    agent = Agent(
        model="deepseek/deepseek-chat",
        name="coach_agent",
        description="Running coach assistant powered by Strava and Garmin data",
        instruction=COACH_INSTRUCTION,
        tools=[
            strava_tools.get_recent_activities,
            strava_tools.get_activity_detail,
            strava_tools.get_athlete_stats,
            strava_tools.get_training_load,
            strava_tools.get_segment_efforts,
            garmin_tools.get_health_snapshot,
            garmin_tools.get_sleep_data,
            garmin_tools.get_heart_rate,
            garmin_tools.get_training_status,
            garmin_tools.get_activity_list,
            memory_tools.remember_fact,
            memory_tools.recall_information,
            memory_tools.get_user_profile,
            running_tools.calculate_pace,
            running_tools.predict_race_time,
            running_tools.calculate_splits,
            running_tools.training_zones,
        ],
    )
    return agent
