from typing import Any, Dict, Optional


class SmartlockInstance:
    """Represents a single smartlock and its instance-level operations."""

    def __init__(self, client, smartlock_id: int, data: Optional[Dict[str, Any]] = None):
        self.client = client
        self.id = smartlock_id
        self._data = data or {}

        # Hex representation of smartlock ID for convenience
        self.hex_id = f"{smartlock_id:x}"[1:].upper()

    # --- Metadata properties ---
    @property
    def name(self) -> Optional[str]:
        return self._data.get("name") or self._data.get("config", {}).get("name")

    @property
    def state(self) -> Optional[Dict[str, Any]]:
        return self._data.get("state")

    @property
    def battery_charge(self) -> int | None:
        state = self._data.get("state", {})
        return state.get("batteryCharge")

    @property
    def is_locked(self) -> bool:
        state = self._data.get("state", {})
        return state.get("state") == 1

    # --- Data sync ---
    def refresh(self) -> Dict[str, Any]:
        """Fetch the latest data for this smartlock.
        """
        self._data = self.client._request("GET", f"/smartlock/{self.id}")
        return self._data

    # --- Convenience actions ---
    def _action(self, action: int) -> Dict[str, Any]:
        """Send an action to this smartlock.

        POST /smartlock/{smartlockId}/action
        """
        payload = {"action": action}
        return self.client._request(
            "POST", f"/smartlock/{self.id}/action", json=payload
        )

    def lock(self, full: bool = False) -> Dict[str, Any]:
        """Lock or full lock the smartlock."""
        return self._action(6 if full else 2)

    def unlock(self) -> Dict[str, Any]:
        """Unlock the smartlock."""
        return self._action(1)

    def unlatch(self) -> Dict[str, Any]:
        """Unlatch the smartlock."""
        return self._action(3)

    def lock_and_go(self, unlatch: bool = False) -> Dict[str, Any]:
        """Lock ’n’ Go, optionally with unlatch."""
        return self._action(5 if unlatch else 4)

