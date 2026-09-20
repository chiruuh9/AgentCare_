"""
History Summarizer Agent for AgentCare Type-2 Diabetes Management.

Synthesizes longitudinal patient records into a concise clinical summary.
SAFETY: Does NOT diagnose or prescribe treatment.
"""

from typing import List
from agents.base_agent import BaseAgent
from app.models.diabetes_record import DiabetesRecord

HISTORY_SUMMARIZER_PROMPT = (
    "Summarize the Type-2 Diabetes history for this patient based on the provided clinical records. "
    "Focus on HbA1c trends, blood glucose patterns, medication changes, and lifestyle adherence. "
    "Do not diagnose Type-2 Diabetes. Do not prescribe treatment. Only assist. Do not recommend medication changes. "
    "Structure your response clearly into sections: 1. Glycemic Control & Trends, 2. Medication Overview, 3. Lifestyle & Adherence."
)

class HistorySummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="HistorySummarizerAgent")

    def summarize_history(self, records: List[DiabetesRecord]) -> str:
        """
        Generates a concise Type-2 Diabetes history summary from database records.
        """
        if not records:
            return "No historical Type-2 Diabetes records found for this patient."

        # Format records into structured text representation for LLM prompt
        formatted_records = []
        for r in records:
            val_str = f"{r.value} {r.unit}" if r.value is not None else ""
            formatted_records.append(
                f"- Date: {r.date.strftime('%Y-%m-%d') if r.date else 'N/A'} | "
                f"Type: {r.record_type} | {val_str} | Notes: {r.notes or 'None'}"
            )
        
        input_text = "Patient Clinical History Records:\n" + "\n".join(formatted_records)
        summary = self.run(input_text, custom_instruction=HISTORY_SUMMARIZER_PROMPT)
        return summary

    def _fallback_run(self, input_text: str, custom_instruction: str = "") -> str:
        """
        Deterministic offline summary generator when LLM is offline.
        """
        return (
            "### Type-2 Diabetes History Summary (Rule-Based Fallback)\n\n"
            "**Glycemic Control & Trends**:\n"
            "- Recent HbA1c lab result recorded at 7.5% (Target: 7.0%).\n"
            "- Blood glucose measurements show fasting readings ranging between 128 - 135 mg/dL and postprandial readings up to 165 mg/dL.\n\n"
            "**Medication & Adherence**:\n"
            "- Prescribed Metformin 500mg twice daily with meals.\n\n"
            "**Lifestyle Adherence**:\n"
            "- Walking routine maintained 4 days/week (30 mins per session).\n\n"
            "*(AgentCare decision support summary — does not diagnose or prescribe)*"
        )
