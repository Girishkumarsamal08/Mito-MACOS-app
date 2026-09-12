# type: ignore
# BACKEND/providers/ExotelProvider.py

"""
Exotel Telephony Provider for MITO.
Implements Exotel REST API for Indian outbound calling compliant with DoT / TRAI regulations.
"""

import os
import requests
from typing import Dict, Any, Optional
from BACKEND.TelephonyProvider import BaseTelephonyProvider

class ExotelProvider(BaseTelephonyProvider):
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, api_key: Optional[str] = None):
        self.account_sid = account_sid or os.getenv("EXOTEL_ACCOUNT_SID") or os.getenv("TELEPHONY_ACCOUNT_ID")
        self.auth_token = auth_token or os.getenv("EXOTEL_AUTH_TOKEN") or os.getenv("TELEPHONY_AUTH_TOKEN")
        self.api_key = api_key or os.getenv("EXOTEL_API_KEY")
        self.base_url = f"https://api.exotel.com/v1/Accounts/{self.account_sid}" if self.account_sid else ""

    def validate_credentials(self) -> bool:
        if not self.account_sid or not self.auth_token:
            return False
        return True

    def make_outbound_call(
        self,
        to_number: str,
        from_number: str,
        reason: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.validate_credentials():
            return {
                "success": False,
                "call_id": "",
                "status": "failed",
                "error": "Missing Exotel credentials"
            }

        url = f"{self.base_url}/Calls/connect.json"
        payload = {
            "From": from_number,
            "To": to_number,
            "CallerId": from_number,
            "CallType": "trans",
            "TimeLimit": "300"
        }
        if callback_url:
            payload["StatusCallback"] = callback_url

        try:
            resp = requests.post(
                url,
                data=payload,
                auth=(self.api_key or self.account_sid, self.auth_token),
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                call_info = data.get("Call", {})
                call_sid = call_info.get("Sid", "")
                status = call_info.get("Status", "queued")
                print(f"[ExotelProvider] Outbound call initiated to {to_number}. Call SID: {call_sid}")
                return {
                    "success": True,
                    "call_id": call_sid,
                    "status": status,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "call_id": "",
                    "status": "failed",
                    "error": f"Exotel API error {resp.status_code}: {resp.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "call_id": "",
                "status": "failed",
                "error": str(e)
            }

    def hangup_call(self, call_id: str) -> bool:
        return True

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        if not self.account_sid or not call_id:
            return {"status": "failed", "answered": False, "duration_seconds": 0}
        
        url = f"{self.base_url}/Calls/{call_id}.json"
        try:
            resp = requests.get(
                url,
                auth=(self.api_key or self.account_sid, self.auth_token),
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json().get("Call", {})
                status = data.get("Status", "unknown")
                duration = int(data.get("Duration") or 0)
                answered = status == "completed" and duration > 0
                return {
                    "status": status,
                    "answered": answered,
                    "duration_seconds": duration
                }
        except Exception as e:
            print(f"[ExotelProvider Status Error] {e}")

        return {"status": "failed", "answered": False, "duration_seconds": 0}
