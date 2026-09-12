# type: ignore
# BACKEND/providers/TwilioProvider.py

"""
Twilio Telephony Provider for MITO.
Implements official Twilio REST API for outbound voice calling to Indian destination numbers (+91).
Supports verified Caller ID, TwiML Media Streams for Gemini Live, and call status tracking.
"""

import os
import requests
from typing import Dict, Any, Optional
from BACKEND.TelephonyProvider import BaseTelephonyProvider

class TwilioProvider(BaseTelephonyProvider):
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None):
        self.account_sid = account_sid or os.getenv("TELEPHONY_ACCOUNT_ID") or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TELEPHONY_AUTH_TOKEN") or os.getenv("TWILIO_AUTH_TOKEN")
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}" if self.account_sid else ""

    def validate_credentials(self) -> bool:
        if not self.account_sid or not self.auth_token:
            print("[TwilioProvider Error] Account SID or Auth Token missing.")
            return False
        try:
            resp = requests.get(
                f"{self.base_url}.json",
                auth=(self.account_sid, self.auth_token),
                timeout=5
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[TwilioProvider Credential Check Error] {e}")
            return False

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
                "error": "Invalid or missing Twilio credentials"
            }

        url = f"{self.base_url}/Calls.json"
        
        if callback_url:
            twiml = f'<Response><Connect><Stream url="{callback_url}"/></Connect></Response>'
            data = {
                "To": to_number,
                "From": from_number,
                "Twiml": twiml,
                "Timeout": "25",
                "MachineDetection": "Enable"
            }
        else:
            twiml = f'<Response><Say voice="Polly.Aditi">Hello sir, this is MITO.</Say></Response>'
            data = {
                "To": to_number,
                "From": from_number,
                "Twiml": twiml,
                "Timeout": "25"
            }

        try:
            response = requests.post(
                url,
                data=data,
                auth=(self.account_sid, self.auth_token),
                timeout=10
            )
            if response.status_code in [200, 201]:
                res_data = response.json()
                call_sid = res_data.get("sid", "")
                status = res_data.get("status", "queued")
                print(f"[TwilioProvider] Outbound call initiated to {to_number}. Call SID: {call_sid}")
                return {
                    "success": True,
                    "call_id": call_sid,
                    "status": status,
                    "error": None
                }
            else:
                err_msg = f"Twilio API Error {response.status_code}: {response.text}"
                print(f"[TwilioProvider] {err_msg}")
                return {
                    "success": False,
                    "call_id": "",
                    "status": "failed",
                    "error": err_msg
                }
        except Exception as e:
            print(f"[TwilioProvider Error] {e}")
            return {
                "success": False,
                "call_id": "",
                "status": "failed",
                "error": str(e)
            }

    def hangup_call(self, call_id: str) -> bool:
        if not self.account_sid or not call_id:
            return False
        url = f"{self.base_url}/Calls/{call_id}.json"
        try:
            resp = requests.post(
                url,
                data={"Status": "completed"},
                auth=(self.account_sid, self.auth_token),
                timeout=5
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[TwilioProvider Hangup Error] {e}")
            return False

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        if not self.account_sid or not call_id:
            return {"status": "failed", "answered": False, "duration_seconds": 0}
        
        url = f"{self.base_url}/Calls/{call_id}.json"
        try:
            resp = requests.get(
                url,
                auth=(self.account_sid, self.auth_token),
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                duration = int(data.get("duration") or 0)
                answered = status in ["in-progress", "completed"] and duration > 0
                return {
                    "status": status,
                    "answered": answered,
                    "duration_seconds": duration
                }
        except Exception as e:
            print(f"[TwilioProvider Status Error] {e}")

        return {"status": "failed", "answered": False, "duration_seconds": 0}
