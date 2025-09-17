class Opener:
    """Sub-client for managing intercom/openers."""

    def __init__(self, client):
        self.client = client

    # ---- Intercom Brands ----
    def list_brands(self):
        """Get all intercom brands."""
        return self.client._request("GET", "/opener/brand")

    def get_brand(self, brand_id):
        """Get a specific intercom brand."""
        return self.client._request("GET", f"/opener/brand/{brand_id}")

    # ---- Intercom Models ----
    def list_intercoms(self):
        """Get a list of intercom models."""
        return self.client._request("GET", "/opener/intercom")

    def get_intercom(self, intercom_id):
        """Get a specific intercom model."""
        return self.client._request("GET", f"/opener/intercom/{intercom_id}")