# type: ignore
# BACKEND/CallManager.py

"""
Call Manager for MITO Proactive Personal Phone Calling System.
Responsible for:
- Evaluating Proactive Contact Policy (consent, quiet hours, daily limits, cooldown)
- AURA pre-call evaluation
- Provider lifecycle & call tracking
- Recording call history in Data/call_history.json
- Unanswered call memory management (NO automated retries)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv, dotenv_values

from AURA.aura_controller import AURAController
from BACKEND.TelephonyProvider import BaseTelephonyProvider
from BACKEND.providers.TwilioProvider import TwilioProvider
from BACKEND.providers.ExotelProvider import ExotelProvider
from BACKEND.providers.MockProvider import MockTelephonyProvider

load_dotenv()
env_vars = dotenv_values(".env")

CALL_HISTORY_FILE = "Data/call_history.json"

class CallManager:
    def __init__(self):
        self.aura = AURAController()
        self.provider: Optional[BaseTelephonyProvider] = None
        self._init_provider()

    def _init_provider(self):
        provider_name = (os.getenv("TELEPHONY_PROVIDER") or env_vars.get("TELEPHONY_PROVIDER") or "mock").lower().strip()
        if provider_name == "twilio":
            self.provider = TwilioProvider()
        elif provider_name == "exotel":
            self.provider = ExotelProvider()
        elif provider_name == "mock":
            self.provider = MockTelephonyProvider(simulate_answer=False, simulate_status="no_answer")
        else:
            print(f"[CallManager Warning] Unknown provider '{provider_name}'. Defaulting to MockTelephonyProvider.")
            self.provider = MockTelephonyProvider(simulate_answer=False, simulate_status="no_answer")

    # -----------------------------
    # CONFIGURATION & HISTORY HELPERS
    # -----------------------------
    @property
    def is_enabled(self) -> bool:
        allow_val = os.getenv("ALLOW_PROACTIVE_CALLS") or env_vars.get("ALLOW_PROACTIVE_CALLS") or "false"
        if isinstance(allow_val, bool):
            return allow_val
        return allow_val.lower().strip() in ["true", "1", "yes"]

    @property
    def my_phone_number(self) -> str:
        return (os.getenv("MY_PHONE_NUMBER") or env_vars.get("MY_PHONE_NUMBER") or "").strip()

    @property
    def mito_phone_number(self) -> str:
        return (os.getenv("MITO_PHONE_NUMBER") or env_vars.get("MITO_PHONE_NUMBER") or "").strip()

    @property
    def max_calls_per_day(self) -> int:
        try:
            return int(os.getenv("MAX_PROACTIVE_CALLS_PER_DAY") or env_vars.get("MAX_PROACTIVE_CALLS_PER_DAY") or 2)
        except ValueError:
            return 2

    @property
    def min_cooldown_hours(self) -> float:
        try:
            return float(os.getenv("MIN_TIME_BETWEEN_PROACTIVE_CALLS_HOURS") or env_vars.get("MIN_TIME_BETWEEN_PROACTIVE_CALLS_HOURS") or 4.0)
        except ValueError:
            return 4.0

    @property
    def quiet_hours(self) -> Tuple[str, str]:
        start = (os.getenv("QUIET_HOURS_START") or env_vars.get("QUIET_HOURS_START") or "23:00").strip()
        end = (os.getenv("QUIET_HOURS_END") or env_vars.get("QUIET_HOURS_END") or "08:00").strip()
        return start, end

    def _load_history(self) -> Dict[str, Any]:
        if not os.path.exists(CALL_HISTORY_FILE):
            return {"calls": []}
        try:
            with open(CALL_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "calls" in data:
                    return data
        except Exception as e:
            print(f"[CallManager History Load Error] {e}")
        return {"calls": []}

    def _save_history(self, history: Dict[str, Any]):
        try:
            os.makedirs(os.path.dirname(CALL_HISTORY_FILE), exist_ok=True)
            with open(CALL_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"[CallManager History Save Error] {e}")

    # -----------------------------
    # POLICY EVALUATION
    # -----------------------------
    def _is_quiet_hours(self) -> bool:
        start_str, end_str = self.quiet_hours
        try:
            now = datetime.now().time()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()

            if start_time <= end_time:
                return start_time <= now <= end_time
            else:
                return now >= start_time or now <= end_time
        except Exception as e:
            print(f"[CallManager Quiet Hours Parse Error] {e}")
            return False

    def can_make_proactive_call(self, reason: str, urgency: str = "medium") -> Tuple[bool, str]:
        if not self.is_enabled:
            return False, "Proactive calls are disabled in configuration (ALLOW_PROACTIVE_CALLS=false)."

        if not self.my_phone_number or not self.mito_phone_number:
            return False, "MY_PHONE_NUMBER or MITO_PHONE_NUMBER is not configured."

        if self._is_quiet_hours():
            return False, f"Current time is within configured Quiet Hours ({self.quiet_hours[0]} - {self.quiet_hours[1]})."

        history = self._load_history()
        now_ts = time.time()
        calls = history.get("calls", [])

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        today_calls = [c for c in calls if c.get("timestamp", 0) >= today_start]
        if len(today_calls) >= self.max_calls_per_day:
            return False, f"Daily call limit reached ({len(today_calls)}/{self.max_calls_per_day} calls today)."

        if calls:
            last_call = calls[-1]
            last_ts = last_call.get("timestamp", 0)
            elapsed_hours = (now_ts - last_ts) / 3600.0
            if elapsed_hours < self.min_cooldown_hours:
                return False, f"Cooldown period active ({elapsed_hours:.1f}h / {self.min_cooldown_hours}h elapsed since last call)."

        aura_res = self.aura.evaluate(f"Initiate proactive outbound call for reason: {reason}")
        if aura_res.reject:
            return False, f"AURA policy rejected proactive call trigger (risk score: {aura_res.risk})."

        return True, "Call permitted by policy."

    # -----------------------------
    # CALL LIFECYCLE MANAGEMENT
    # -----------------------------
    def make_call(self, reason: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        allowed, policy_msg = self.can_make_proactive_call(reason)
        if not allowed:
            print(f"[CallManager Blocked] {policy_msg}")
            return {
                "success": False,
                "reason": reason,
                "status": "blocked",
                "message": policy_msg
            }

        if not self.provider:
            return {
                "success": False,
                "reason": reason,
                "status": "error",
                "message": "Telephony provider not initialized."
            }

        print(f"[CallManager] Initiating proactive call for reason: '{reason}'...")
        call_res = self.provider.make_outbound_call(
            to_number=self.my_phone_number,
            from_number=self.mito_phone_number,
            reason=reason
        )

        call_id = call_res.get("call_id", "")
        status = call_res.get("status", "failed")
        success = call_res.get("success", False)

        if isinstance(self.provider, MockTelephonyProvider):
            status_info = self.provider.get_call_status(call_id)
            answered = status_info.get("answered", False)
            duration = status_info.get("duration_seconds", 0)
            status = status_info.get("status", status)
        else:
            answered = status in ["in-progress", "completed"]
            duration = 0

        record = self.record_call_result(
            call_id=call_id,
            reason=reason,
            status=status,
            answered=answered,
            duration_seconds=duration,
            notes=context.get("notes", "") if context else ""
        )

        return {
            "success": success,
            "call_id": call_id,
            "reason": reason,
            "status": status,
            "answered": answered,
            "history_record": record
        }

    def record_call_result(
        self,
        call_id: str,
        reason: str,
        status: str,
        answered: bool,
        duration_seconds: int = 0,
        notes: str = ""
    ) -> Dict[str, Any]:
        history = self._load_history()
        record = {
            "timestamp": time.time(),
            "iso_time": datetime.now().isoformat(),
            "call_id": call_id,
            "reason": reason,
            "status": status,
            "answered": answered,
            "duration_seconds": duration_seconds,
            "notes": notes or ("No answer" if not answered else "Answered by user")
        }
        history["calls"].append(record)
        self._save_history(history)
        print(f"[CallManager History] Recorded call outcome: {status} (Answered: {answered})")
        return record

    def get_recent_unanswered_call(self, max_age_hours: float = 12.0) -> Optional[Dict[str, Any]]:
        history = self._load_history()
        calls = history.get("calls", [])
        if not calls:
            return None

        now_ts = time.time()
        for call in reversed(calls):
            if not call.get("answered", False):
                call_ts = call.get("timestamp", 0)
                age_hours = (now_ts - call_ts) / 3600.0
                if age_hours <= max_age_hours:
                    return {
                        "timestamp": call_ts,
                        "age_minutes": int((now_ts - call_ts) / 60),
                        "reason": call.get("reason", "unknown"),
                        "status": call.get("status", "no_answer")
                    }
        return None
