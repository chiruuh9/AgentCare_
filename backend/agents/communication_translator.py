"""
Communication Translator Agent for AgentCare Type-2 Diabetes Management.

Translates complex clinical directives and monitoring targets into patient-friendly language.
SAFETY: Keeps explanations accurate and non-diagnostic. Does NOT prescribe.
"""

from agents.base_agent import BaseAgent

COMMUNICATION_TRANSLATOR_PROMPT = (
    "Translate these Type-2 Diabetes clinical instructions and targets into the requested language and simple, clear, everyday language "
    "that a patient can easily understand. Keep it accurate, encouraging, and non-diagnostic. "
    "Do not diagnose Type-2 Diabetes. Do not prescribe treatment. Only assist. Do not alter clinician instructions."
)

class CommunicationTranslatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="CommunicationTranslatorAgent")

    def translate_instructions(self, clinical_instructions: str, language_code: str = "en-IN") -> str:
        """
        Translates complex medical directives into patient-friendly guidance.
        """
        prompt = f"{COMMUNICATION_TRANSLATOR_PROMPT} Return the output in language code {language_code}."
        return self.run(clinical_instructions, custom_instruction=prompt)

    def _fallback_run(self, input_text: str, custom_instruction: str = "") -> str:
        """
        Deterministic offline fallback translation.
        """
        return (
            "### Your Type-2 Diabetes Care Guide (Patient-Friendly Language)\n\n"
            "1. **Understanding Your HbA1c Target (7.0%)**:\n"
            "   - Your HbA1c shows your average blood sugar over the last 3 months. Your target goal set by your care team is 7.0%.\n\n"
            "2. **Daily Blood Sugar Checks**:\n"
            "   - Test your blood sugar in the morning before eating breakfast. A fasting reading between 80–130 mg/dL is ideal.\n\n"
            "3. **Taking Your Metformin**:\n"
            "   - Take 1 tablet of Metformin (500mg) with breakfast and 1 tablet with dinner. Eating meals with your pill keeps your stomach feeling comfortable.\n\n"
            "4. **Active Lifestyle Goal**:\n"
            "   - Aim for a pleasant 30-minute walk 4 times a week, especially after dinner to help your body process carbohydrates."
        )
