class Service:
    """Sub-client for managing services."""

    def __init__(self, client):
        self.client = client

    # ---- Services ----
    def list_services(self):
        """Get a list of services.

        GET /service
        """
        return self.client._request("GET", "/service")

    def get_service(self, service_id):
        """Get a specific service.

        GET /service/{serviceId}
        """
        return self.client._request("GET", f"/service/{service_id}")

    def link_service(self, service_id, data=None):
        """Link a service.

        POST /service/{serviceId}/link
        """
        return self.client._request(
            "POST", f"/service/{service_id}/link", json=data or {}
        )

    def sync_service(self, service_id, data=None):
        """Sync a service.

        POST /service/{serviceId}/sync
        """
        return self.client._request(
            "POST", f"/service/{service_id}/sync", json=data or {}
        )

    def unlink_service(self, service_id, data=None):
        """Unlink a service.

        POST /service/{serviceId}/unlink
        """
        return self.client._request(
            "POST", f"/service/{service_id}/unlink", json=data or {}
        )