from typing import Any, Dict, Optional


class SmartlockLog:
    """Sub-client for retrieving smartlock logs."""

    def __init__(self, client):
        self.client = client

    # ---- Account-level logs ----
    def list_logs(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a list of smartlock logs for all smartlocks.

        GET /smartlock/log
        """
        return self.client._request("GET", "/smartlock/log", params=params)

    # ---- Smartlock-specific logs ----
    def list_logs_for_smartlock(self, smartlock_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a list of smartlock logs for a specific smartlock.

        GET /smartlock/{smartlockId}/log
        """
        return self.client._request("GET", f"/smartlock/{smartlock_id}/log", params=params)