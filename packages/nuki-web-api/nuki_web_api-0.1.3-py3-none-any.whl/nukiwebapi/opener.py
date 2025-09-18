class Opener:
    """Sub-client for managing intercom/openers."""

    def __init__(self, client):
        self.client = client

    # ---- Intercom Brands ----
    def list_brands(self):
        """Get all intercom brands.

        GET /opener/brand
        """
        return self.client._request("GET", "/opener/brand")

    def get_brand(self, brand_id):
        """Get a specific intercom brand.

        GET /opener/brand/{brandId}
        """
        return self.client._request("GET", f"/opener/brand/{brand_id}")

    # ---- Intercom Models ----
    def list_intercoms(self):
        """Get a list of intercom models.

        GET /opener/intercom
        """
        return self.client._request("GET", "/opener/intercom")

    def get_intercom(self, intercom_id):
        """Get a specific intercom model.

        GET /opener/intercom/{intercomId}
        """
        return self.client._request("GET", f"/opener/intercom/{intercom_id}")