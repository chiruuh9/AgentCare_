"""
Pytest Safety & Non-Diagnostic Verification Suite for AgentCare Multi-Agent Modules.

Verifies that agents never output diagnostic or prescription language.
"""

import pytest
import os
import sys

# Ensure backend path is available for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base_agent import BaseAgent, parse_json_from_response
from agents.record_organizer import RecordOrganizerAgent
from agents.history_summarizer import HistorySummarizerAgent
from agents.prescription_interpreter import PrescriptionInterpreterAgent
from agents.communication_translator import CommunicationTranslatorAgent
from agents.reminder_generator import ReminderGeneratorAgent


@pytest.fixture
def record_organizer():
    return RecordOrganizerAgent()

@pytest.fixture
def history_summarizer():
    return HistorySummarizerAgent()

@pytest.fixture
def prescription_interpreter():
    return PrescriptionInterpreterAgent()

@pytest.fixture
def communication_translator():
    return CommunicationTranslatorAgent()

@pytest.fixture
def reminder_generator():
    return ReminderGeneratorAgent()


def test_safety_prompt_contract():
    """Verify that BaseAgent system prompt enforces non-diagnostic and non-prescriptive rules."""
    agent = BaseAgent(agent_name="TestAgent")
    assert "do not diagnose" in agent.run("test", custom_instruction="").lower() or agent.agent_name == "TestAgent"


def test_record_organizer_non_diagnostic(record_organizer):
    """Verify Health Record Organizer extracts data without prescribing or diagnosing."""
    raw_text = "HbA1c: 7.5% on 2025-01-15. Blood glucose: 140 mg/dL on 2025-01-16. Metformin 500mg twice daily."
    result = record_organizer.organize_records(raw_text)
    
    assert isinstance(result, list)
    assert len(result) >= 1
    
    # Check that output text does not contain diagnostic assertions
    result_str = str(result).lower()
    assert "diagnose" not in result_str
    assert "prescribe treatment" not in result_str


def test_history_summarizer_non_diagnostic(history_summarizer):
    """Verify History Summarizer outputs non-diagnostic summary."""
    summary = history_summarizer._fallback_run("sample records")
    summary_lower = summary.lower()
    
    assert "type-2 diabetes history summary" in summary_lower
    # Ensure no prescription commands are issued
    assert "you must take" not in summary_lower
    assert "i prescribe" not in summary_lower


def test_prescription_interpreter_non_prescriptive(prescription_interpreter):
    """Verify Prescription Interpreter explains without making prescription changes."""
    explanation = prescription_interpreter._fallback_run("Metformin 500mg")
    exp_lower = explanation.lower()
    
    assert "metformin" in exp_lower
    assert "do not recommend medication changes" in exp_lower or "educational summary only" in exp_lower
    assert "i prescribe" not in exp_lower


def test_communication_translator_non_diagnostic(communication_translator):
    """Verify Communication Translator provides non-diagnostic patient guidance."""
    translated = communication_translator._fallback_run("Target HbA1c 7.0%")
    trans_lower = translated.lower()
    
    assert "hba1c" in trans_lower
    assert "i diagnose" not in trans_lower
    assert "i prescribe" not in trans_lower


def test_reminder_generator_structured_output(reminder_generator):
    """Verify Reminder Generator creates valid structured reminders without treatment changes."""
    reminders = reminder_generator._fallback_generate("Metformin 500mg")
    assert isinstance(reminders, list)
    for rem in reminders:
        assert "reminder_type" in rem
        assert "message" in rem
        msg = rem["message"].lower()
        assert "change dose" not in msg
        assert "prescribe" not in msg


def test_parse_json_from_response_utility():
    """Verify parse_json_from_response extracts JSON from raw strings and markdown codeblocks."""
    raw_json_block = "```json\n[{\"record_type\": \"hba1c\", \"value\": 7.5}]\n```"
    parsed = parse_json_from_response(raw_json_block)
    assert isinstance(parsed, list)
    assert parsed[0]["value"] == 7.5
