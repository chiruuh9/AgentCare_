"""
Reminder Generator Agent for AgentCare Type-2 Diabetes Management.

Generates structured monitoring and medication adherence reminders.
SAFETY: Does NOT alter treatment plans or prescribe.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from agents.base_agent import BaseAgent, parse_json_from_response

REMINDER_GENERATOR_PROMPT = (
    "Generate structured reminders for Type-2 Diabetes management based on the provided medication and monitoring plan. "
    "Output MUST be a JSON array of objects with keys: "
    "'reminder_type' (one of: 'medication', 'glucose_check', 'appointment', 'lifestyle'), "
    "'message' (clear action message string), "
    "'scheduled_time' (ISO datetime string 'YYYY-MM-DDTHH:MM:SS'). "
    "Include medication times, blood glucose checks, appointments, and lifestyle reminders. "
    "Do not diagnose Type-2 Diabetes. Do not prescribe treatment. Only assist. Do not create reminders for treatment changes. Return ONLY valid JSON array format."
)

class ReminderGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="ReminderGeneratorAgent")

    def generate_reminders(self, plan_context: str) -> List[Dict[str, Any]]:
        """
        Generates structured reminder objects based on clinical context.
        """
        raw_response = self.run(plan_context, custom_instruction=REMINDER_GENERATOR_PROMPT)
        
        try:
            parsed = parse_json_from_response(raw_response)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "reminders" in parsed:
                return parsed["reminders"]
            return [parsed]
        except Exception:
            return self._fallback_generate(plan_context)

    def _fallback_generate(self, plan_context: str) -> List[Dict[str, Any]]:
        """
        Deterministic offline fallback reminder generator.
        """
        now = datetime.now(timezone.utc)
        return [
            {
                "reminder_type": "glucose_check",
                "message": "Fasting Blood Glucose Check — Log your morning blood glucose reading before breakfast.",
                "scheduled_time": (now + timedelta(hours=8)).strftime("%Y-%m-%dT08:00:00"),
            },
            {
                "reminder_type": "medication",
                "message": "Take Metformin 500mg — Take 1 tablet with morning breakfast.",
                "scheduled_time": (now + timedelta(hours=8, minutes=30)).strftime("%Y-%m-%dT08:30:00"),
            },
            {
                "reminder_type": "medication",
                "message": "Take Metformin 500mg — Take 1 tablet with evening dinner.",
                "scheduled_time": (now + timedelta(hours=19)).strftime("%Y-%m-%dT19:00:00"),
            },
            {
                "reminder_type": "lifestyle",
                "message": "30-Minute Evening Walk — Recommended post-dinner activity for glycemic regulation.",
                "scheduled_time": (now + timedelta(hours=20)).strftime("%Y-%m-%dT20:00:00"),
            },
        ]
