"""
Base Agent Class for AgentCare Multi-Agent Clinical Support Suite.

SAFETY NOTICE:
All agents derived from BaseAgent MUST preserve non-diagnostic and non-prescriptive safety constraints.
"""

import os
import re
import json
import logging
from typing import Any, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.middleware.audit_logging import log_agent_action

logger = logging.getLogger("agentcare.agents")

SAFETY_SYSTEM_PROMPT = (
    "You are an AI assistant for Type-2 Diabetes management. "
    "You do not diagnose Type-2 Diabetes or any disease. "
    "You do not prescribe treatment or medication changes. "
    "You only assist with organizing records, summarizing history, "
    "interpreting prescriptions, translating instructions, and generating reminders."
)


def parse_json_from_response(text: str) -> Union[dict, list]:
    """
    Utility function to extract and parse JSON objects or arrays from LLM response text,
    handling markdown codeblocks (```json ... ```) and raw string formatting.
    """
    cleaned = text.strip()
    
    # Strip markdown fenced codeblocks if present
    if "```" in cleaned:
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: attempt regex extraction of array or object
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse valid JSON from LLM response: {text[:200]}")


class BaseAgent:
    """
    Base Agent for Type-2 Diabetes Management.
    Configurable to use OpenAI or local LLM fallback based on environment configuration.
    """

    def __init__(self, agent_name: str = "BaseAgent", model_name: str = "gpt-4o-mini"):
        self.agent_name = agent_name
        self.api_key = settings.OPENAI_API_KEY
        
        # Swappable model support (e.g. OpenAI GPT models or local Ollama / LM Studio endpoint)
        local_llm_url = os.getenv("LOCAL_LLM_URL", "")
        
        if local_llm_url:
            logger.info(f"[{self.agent_name}] Initializing with local LLM endpoint: {local_llm_url}")
            self.llm = ChatOpenAI(
                base_url=local_llm_url,
                api_key="local-llm-key",
                model_name=os.getenv("LOCAL_LLM_MODEL", "llama3"),
                temperature=0.1,
            )
        elif self.api_key and self.api_key != "your_openai_api_key_here":
            logger.info(f"[{self.agent_name}] Initializing with OpenAI model: {model_name}")
            self.llm = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=model_name,
                temperature=0.1,
            )
        else:
            logger.warning(f"[{self.agent_name}] OPENAI_API_KEY not provided. Using offline rule-based fallback mode.")
            self.llm = None

    def run(self, input_text: str, custom_instruction: str = "") -> str:
        """
        Executes LLM request with safety prompt and custom instructions.
        """
        log_agent_action(self.agent_name, patient_id=0, action="run", details=input_text)
        
        # If no LLM available, call fallback handler
        if self.llm is None:
            return self._fallback_run(input_text, custom_instruction)

        messages = [
            SystemMessage(content=f"{SAFETY_SYSTEM_PROMPT}\n{custom_instruction}"),
            HumanMessage(content=input_text),
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error invoking LLM: {e}. Falling back to offline rule handler.")
            return self._fallback_run(input_text, custom_instruction)

    def _fallback_run(self, input_text: str, custom_instruction: str = "") -> str:
        """
        Offline fallback implementation when LLM API keys are unavailable.
        Override in specific agents to provide deterministic offline responses for testing.
        """
        return f"[Agent: {self.agent_name}] Input received for processing. Safety constraints enforced."
