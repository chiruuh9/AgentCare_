"""
Prescription Interpreter Agent for AgentCare Type-2 Diabetes Management.

Provides plain-language explanations of prescribed Type-2 Diabetes medications.
SAFETY: Does NOT recommend medication changes or prescribe treatments.
"""

from typing import List
from agents.base_agent import BaseAgent
from app.models.medication import Medication

PRESCRIPTION_INTERPRETER_PROMPT = (
    "Explain the following Type-2 Diabetes prescription in simple, patient-friendly terms. "
    "For each medication listed, explain: 1. What it is for, 2. How to take it properly, 3. Common side effects to watch for. "
    "Do not diagnose Type-2 Diabetes. Do not prescribe treatment. Only assist. Do not recommend medication changes or dosage alterations."
)

class PrescriptionInterpreterAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="PrescriptionInterpreterAgent")

    def interpret_prescriptions(self, medications: List[Medication], raw_prescription_text: str = "") -> str:
        """
        Generates simple explanations for prescribed Type-2 Diabetes medications.
        """
        med_strings = []
        for m in medications:
            med_strings.append(
                f"- Medication: {m.name} {m.dosage} | Frequency: {m.frequency} | Prescriber: {m.prescribing_doctor}"
            )
        
        combined_text = "Current Prescribed Medications:\n" + "\n".join(med_strings)
        if raw_prescription_text:
            combined_text += f"\nAdditional Prescription Notes:\n{raw_prescription_text}"

        return self.run(combined_text, custom_instruction=PRESCRIPTION_INTERPRETER_PROMPT)

    def _fallback_run(self, input_text: str, custom_instruction: str = "") -> str:
        """
        Deterministic offline fallback explanation.
        """
        return (
            "### Type-2 Diabetes Medication Guide (Rule-Based Explanation)\n\n"
            "**1. Metformin 500mg**\n"
            "- **What it is for**: Metformin is a first-line oral medication that helps lower blood glucose levels by reducing sugar production in the liver and improving insulin sensitivity.\n"
            "- **How to take it**: Take 1 tablet (500mg) twice daily with meals (breakfast & dinner) to reduce stomach upset.\n"
            "- **Common Side Effects**: Mild stomach discomfort or nausea when starting. Take with meals to minimize.\n\n"
            "*(Educational summary only — consult your prescribing clinician before making any changes)*"
        )
