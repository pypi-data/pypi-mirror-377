from typing import Any, Dict, Optional


class Smartlock:
    """Sub-client for managing smartlocks."""
    
    def __init__(self, client, smartlock_id, data=None):
        self.client = client
        self.smartlock_id = smartlock_id

        """The hexadecimal representation of the smartlock ID.
        It prepends 1-5 depending on the type of the lock.
        Nuki Web API shows only the actual hex ID, omitting the first digit of the Hex ID.
        
        E.g. smartlock ID 21913877581 = hex 51A2B3C4D = hex ID 1A2B3C4D
        
        The hex_id is to be seen merely as a helper to identify a smartlock more easily,
        the API only relies on the smartlock_id in decimal format as the identifier of
        the smartlock.
        """
        self.smartlock_hex_id = f'{smartlock_id:x}'[1:].upper()
        self._data = data or {}


    # --- Metadata properties ---

    @property
    def name(self) -> Optional[str]:
        return self._data.get("name") or self._data.get("config", {}).get("name")

    @property
    def state(self) -> Optional[Dict[str, Any]]:
        return self._data.get("state")

    @property
    def battery_charge(self) -> Optional[int]:
        state = self._data.get("state", {})
        return state.get("batteryCharge")

    @property
    def is_locked(self) -> Optional[bool]:
        """State=1 means locked, 0 unlocked (per API docs)."""
        state = self._data.get("state", {})
        return state.get("state") == 1

    # --- Data sync ---

    def refresh(self) -> Dict[str, Any]:
        """Fetch the latest smartlock data from the API and update object."""
        data = self.client._request("GET", f"/smartlock/{self.smartlock_id}")
        self._data = data
        return data
    # ------------------------
    # Convenience methods (bound instance)
    # ------------------------
    
   
    def _action(self, smartlock_id: str, action: int) -> Dict[str, Any]:
       
        payload = {"action": action}
        return self.client._request(
            "POST",
            f"/smartlock/{smartlock_id}/action",
            json=payload
        )


    def lock(self, full: bool = False) -> Dict[str, Any]:
        """Lock or full lock the smartlock."""
        if not self.smartlock_id:
            raise ValueError("smartlock_id not set")
        return self._action(self.smartlock_id, 6 if full else 2)

    def unlock(self) -> Dict[str, Any]:
        """Unlock the smartlock."""
        if not self.smartlock_id:
            raise ValueError("smartlock_id not set")
        return self._action(self.smartlock_id, "1")

    def unlatch(self) -> Dict[str, Any]:
        """Unlatch the smartlock."""
        if not self.smartlock_id:
            raise ValueError("smartlock_id not set")
        return self._action(self.smartlock_id, 3)

    def lock_and_go(self, unlatch: bool = False) -> Dict[str, Any]:
        """Lock ’n’ Go, optionally with unlatch."""
        if not self.smartlock_id:
            raise ValueError("smartlock_id not set")
        return self._action(self.smartlock_id, 5 if unlatch else 4)

    # ------------------------
    # General API methods (for any smartlock)
    # ------------------------
    def bulk_web_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", "/bulk-web-config", json=config_data)

    def list_smartlocks(self) -> Dict[str, Any]:
        return self.client._request("GET", "/smartlock")

    def get_smartlock(self, smartlock_id) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("GET", f"/smartlock/{sid}")

    def update_smartlock(self, smartlock_id, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}", json=data or {})

    def delete_smartlock(self, smartlock_id) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("DELETE", f"/smartlock/{sid}")

    def action_smartlock(self, smartlock_id, action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic action for any smartlock ID."""
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/action", json=action_data or {})

    def update_admin_pin(self, smartlock_id, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/admin/pin", json=data or {})

    def update_advanced_config(self, smartlock_id: Optional[str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/advanced/config", json=data or {})

    def update_opener_advanced_config(self, smartlock_id: Optional[str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/advanced/openerconfig", json=data or {})

    def update_smartdoor_advanced_config(self, smartlock_id: Optional[str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/advanced/smartdoorconfig", json=data or {})

    def update_config(self, smartlock_id: Optional[str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/config", json=data or {})

    def sync_smartlock(self, smartlock_id: Optional[str] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/sync")

    def update_web_config(self, smartlock_id: Optional[str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = smartlock_id or self.smartlock_id
        if not sid:
            raise ValueError("smartlock_id not provided")
        return self.client._request("POST", f"/smartlock/{sid}/web/config", json=data or {})