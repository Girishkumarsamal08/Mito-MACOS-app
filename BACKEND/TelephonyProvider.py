# type: ignore
# BACKEND/TelephonyProvider.py

"""
Telephony Provider Interface for MITO.
Abstract base class defining the required contract for legitimate telecom providers.
Supports outbound calling, status polling/webhook tracking, and call disconnection.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTelephonyProvider(ABC):
    """
    Abstract base class for telephony providers (e.g. Twilio, Exotel, Mock).
    """

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate provider API credentials and configuration.
        Returns True if properly configured, False otherwise.
        """
        pass

    @abstractmethod
    def make_outbound_call(
        self,
        to_number: str,
        from_number: str,
        reason: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiates an outbound call to the target phone number.
        Returns a dict containing:
        {
            "success": bool,
            "call_id": str,
            "status": str,  # e.g., "initiated", "queued", "failed"
            "error": Optional[str]
        }
        """
        pass

    @abstractmethod
    def hangup_call(self, call_id: str) -> bool:
        """
        Terminates an active call by ID.
        """
        pass

    @abstractmethod
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Queries current call status from the provider.
        Returns dict with keys: "status" (e.g., "ringing", "in-progress", "completed", "busy", "no-answer", "canceled", "failed"), "duration_seconds"
        """
        pass
