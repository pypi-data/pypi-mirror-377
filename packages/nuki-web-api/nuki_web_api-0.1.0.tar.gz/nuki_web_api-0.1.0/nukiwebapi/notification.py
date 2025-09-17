class Notification:
    """Sub-client for managing notifications."""

    def __init__(self, client):
        self.client = client

    # ---- Notification CRUD ----
    def list_notifications(self):
        """Get all notifications attached to your account."""
        return self.client._request("GET", "/notification")

    def create_notification(self, notification_data):
        """Create a notification configuration."""
        return self.client._request("PUT", "/notification", json=notification_data)

    def get_notification(self, notification_id):
        """Get a specific notification configuration."""
        return self.client._request("GET", f"/notification/{notification_id}")

    def update_notification(self, notification_id, notification_data):
        """Update a notification configuration."""
        return self.client._request("POST", f"/notification/{notification_id}", json=notification_data)

    def delete_notification(self, notification_id):
        """Delete a notification configuration."""
        return self.client._request("DELETE", f"/notification/{notification_id}")