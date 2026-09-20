"""
Health Record Organizer Agent for AgentCare Type-2 Diabetes Management.

Extracts structured records (HbA1c, blood_glucose, medication, lifestyle, history) from raw clinical reports.
SAFETY: Does NOT diagnose or prescribe.
"""

import json
import re
from typing import List, Dict, Any
from datetime import datetime, timezone
from agents.base_agent import BaseAgent, parse_json_from_response

RECORD_ORGANIZER_PROMPT = (
    "Extract Type-2 Diabetes related data from the provided text report into a JSON array of structured records. "
    "Each item in the JSON array must be an object with these exact keys: "
    "'record_type' (one of: 'hba1c', 'blood_glucose', 'medication', 'lifestyle', 'history'), "
    "'value' (number or null), "
    "'unit' (string or null, e.g., '%', 'mg/dL'), "
    "'date' (ISO format date string 'YYYY-MM-DD' or null), "
    "'notes' (brief explanation string). "
    "Do not diagnose Type-2 Diabetes. Do not prescribe treatment. Only assist. Return ONLY valid JSON array format without conversational text."
)

class RecordOrganizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="RecordOrganizerAgent")

    def organize_records(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Parses raw report text and returns structured record dictionaries.
        """
        raw_response = self.run(raw_text, custom_instruction=RECORD_ORGANIZER_PROMPT)
        
        try:
            parsed = parse_json_from_response(raw_response)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "records" in parsed:
                return parsed["records"]
            return [parsed]
        except Exception:
            return self._fallback_organize(raw_text)

    def _fallback_organize(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Deterministic regex fallback for parsing Type-2 Diabetes reports offline.
        """
        records = []
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Match HbA1c
        hba1c_match = re.search(r"HbA1c:\s*([\d\.]+)\s*%", raw_text, re.IGNORECASE)
        if hba1c_match:
            records.append({
                "record_type": "hba1c",
                "value": float(hba1c_match.group(1)),
                "unit": "%",
                "date": today_str,
                "notes": "Extracted HbA1c lab value.",
            })
            
        # Match Blood Glucose
        bg_match = re.search(r"(?:blood glucose|glucose):\s*([\d\.]+)\s*(mg/dL|mmol/L)?", raw_text, re.IGNORECASE)
        if bg_match:
            records.append({
                "record_type": "blood_glucose",
                "value": float(bg_match.group(1)),
                "unit": bg_match.group(2) or "mg/dL",
                "date": today_str,
                "notes": "Extracted blood glucose measurement.",
            })
            
        # Match Metformin or medication
        med_match = re.search(r"(Metformin\s*\d+mg[^\.\n]*)", raw_text, re.IGNORECASE)
        if med_match:
            records.append({
                "record_type": "medication",
                "value": None,
                "unit": None,
                "date": today_str,
                "notes": med_match.group(1).strip(),
            })

        if not records:
            records.append({
                "record_type": "history",
                "value": None,
                "unit": None,
                "date": today_str,
                "notes": f"Raw clinical text recorded: {raw_text[:100]}",
            })

        return records
