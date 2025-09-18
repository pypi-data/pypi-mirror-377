from typing import Dict, Any

from nukiwebapi.smartlock_instance import SmartlockInstance

class Smartlock:
    """Sub-client for collection-level smartlock operations."""

    def __init__(self, client):
        self.client = client

    def list_smartlocks(self) -> Dict[str, Any]:
        """List all smartlocks.

        GET /smartlock
        """
        return self.client._request("GET", "/smartlock")

    def get_smartlock(self, smartlock_id: int) -> SmartlockInstance:
        """Retrieve a single smartlock as an instance.

        GET /smartlock/{smartlockId}
        """
        data = self.client._request("GET", f"/smartlock/{smartlock_id}")
        return SmartlockInstance(self.client, smartlock_id, data)

    def bulk_web_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update web config for multiple smartlocks.

        POST /bulk-web-config
        """
        return self.client._request("POST", "/bulk-web-config", json=config_data)

    def update_smartlock(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update smartlock configuration.

        POST /smartlock/{smartlockId}
        """
        return self.client._request(
            "POST", f"/smartlock/{smartlock_id}", json=data or {}
        )

    def delete_smartlock(self, smartlock_id: int) -> Dict[str, Any]:
        """Delete a smartlock.

        DELETE /smartlock/{smartlockId}
        """
        return self.client._request("DELETE", f"/smartlock/{smartlock_id}")

    def action(self, smartlock_id: int, action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic action for any smartlock ID.

        POST /smartlock/{smartlockId}/action
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/action", json=action_data or {})

    def update_admin_pin(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update admin pin of a smartlock.

        POST /smartlock/{smartlockId}/admin/pin
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/admin/pin", json=data or {})

    def update_advanced_config(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update advanced config for a smartlock.

        POST /smartlock/{smartlockId}/advanced/config
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/advanced/config", json=data or {})

    def update_opener_advanced_config(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update opener advanced config for a smartlock.

        POST /smartlock/{smartlockId}/advanced/openerconfig
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/advanced/openerconfig", json=data or {})

    def update_smartdoor_advanced_config(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update smartdoor advanced config for a smartlock.

        POST /smartlock/{smartlockId}/advanced/smartdoorconfig
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/advanced/smartdoorconfig", json=data or {})

    def update_config(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update smartlock config.

        POST /smartlock/{smartlockId}/config
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/config", json=data or {})

    def sync_smartlock(self, smartlock_id: int) -> Dict[str, Any]:
        """Sync a smartlock.

        POST /smartlock/{smartlockId}/sync
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/sync")

    def update_web_config(self, smartlock_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update web config for a smartlock.

        POST /smartlock/{smartlockId}/web/config
        """
        return self.client._request("POST", f"/smartlock/{smartlock_id}/web/config", json=data or {})
