class Company:
    """Sub-client for managing companies."""

    def __init__(self, client):
        self.client = client

    def list_companies(self):
        """Get a list of companies."""
        # GET /company
        return self.client._request("GET", "/company")
        