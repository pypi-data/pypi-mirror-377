class AddressToken:
    """Sub-client for managing address tokens."""

    def __init__(self, client):
        self.client = client

    def get_token_info(self, token_id):
        """Get info about a specific address token.

        GET /address/token/{tokenId}
        """
        return self.client._request("GET", f"/address/token/{token_id}")

    def get_redeemed_token(self, token_id):
        """Get info about a redeemed address token.

        GET /address/token/{tokenId}/redeem
        """
        return self.client._request("GET", f"/address/token/{token_id}/redeem")

    def redeem_token(self, token_id, payload=None):
        """Redeem an address token.

        POST /address/token/{tokenId}/redeem
        """
        return self.client._request(
            "POST",
            f"/address/token/{token_id}/redeem",
            json=payload or {}
        )

    def list_tokens(self, address_id):
        """Get a list of tokens for a specific address.

        GET /address/{addressId}/token
        """
        return self.client._request("GET", f"/address/{address_id}/token")
