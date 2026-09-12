# type: ignore
# BACKEND/providers/MockProvider.py

"""
Mock Telephony Provider for local testing and validation of MITO call flows.
Simulates call lifecycle (initiated -> ringing -> answered/no-answer/busy -> completed).
"""

import time
import uuid
from typing import Dict, Any, Optional
from BACKEND.TelephonyProvider import BaseTelephonyProvider

class MockTelephonyProvider(BaseTelephonyProvider):
    def __init__(self, simulate_answer: bool = False, simulate_status: str = "no_answer"):
        self.simulate_answer = simulate_answer
        self.simulate_status = simulate_status
        self.calls: Dict[str, Dict[str, Any]] = {}

    def validate_credentials(self) -> bool:
        return True

    def make_outbound_call(
        self,
        to_number: str,
        from_number: str,
        reason: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        call_id = f"mock_{uuid.uuid4().hex[:12]}"
        status = "completed" if self.simulate_answer else self.simulate_status
        
        call_record = {
            "call_id": call_id,
            "to_number": to_number,
            "from_number": from_number,
            "reason": reason,
            "status": status,
            "answered": self.simulate_answer,
            "duration_seconds": 15 if self.simulate_answer else 0,
            "timestamp": time.time()
        }
        self.calls[call_id] = call_record

        print(f"[MockTelephonyProvider] Outbound call simulated to {to_number} from {from_number} (Status: {status})")

        return {
            "success": True,
            "call_id": call_id,
            "status": status,
            "error": None
        }

    def hangup_call(self, call_id: str) -> bool:
        if call_id in self.calls:
            self.calls[call_id]["status"] = "completed"
            return True
        return False

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        if call_id in self.calls:
            call_info = self.calls[call_id]
            return {
                "status": call_info["status"],
                "answered": call_info["answered"],
                "duration_seconds": call_info["duration_seconds"]
            }
        return {
            "status": "failed",
            "answered": False,
            "duration_seconds": 0
        }
