"""
Audit Logging Middleware for AgentCare Type-2 Diabetes Decision Support System.

Logs API endpoints, method, processing time, status code, and safety compliance.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure audit logger
logging.basicConfig(level=logging.INFO)
audit_logger = logging.getLogger("agentcare.audit")

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request entry
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        
        audit_logger.info(f"[AUDIT REQUEST] {method} {path} from {client_host}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Inject safety disclaimer header into response
            response.headers["X-Safety-Disclaimer"] = (
                "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."
            )
            
            audit_logger.info(
                f"[AUDIT RESPONSE] {method} {path} - Status: {response.status_code} - Completed in {process_time:.2f}ms"
            )
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            audit_logger.error(f"[AUDIT ERROR] {method} {path} - Failed with error: {exc} ({process_time:.2f}ms)")
            raise exc


def log_agent_action(agent_name: str, patient_id: int, action: str, details: str = ""):
    """Helper to log multi-agent actions for clinical audit compliance."""
    audit_logger.info(
        f"[AUDIT AGENT] Agent: {agent_name} | Patient ID: {patient_id} | Action: {action} | Context: {details[:100]}"
    )
