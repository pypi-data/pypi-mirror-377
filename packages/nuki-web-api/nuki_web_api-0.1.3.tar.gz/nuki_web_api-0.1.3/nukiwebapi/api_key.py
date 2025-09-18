class ApiKey:
    """Sub-client for managing API keys, advanced keys, and tokens."""

    def __init__(self, client):
        self.client = client

    # ---- API Keys ----
    def list_api_keys(self):
        """List all API keys.

        GET /api/key
        """
        return self.client._request("GET", "/api/key")

    def create_api_key(self, key_data):
        """Create a new API key.

        PUT /api/key
        """
        return self.client._request("PUT", "/api/key", json=key_data)

    def update_api_key(self, api_key_id, key_data):
        """Update an existing API key.

        POST /api/key/{apiKeyId}
        """
        return self.client._request("POST", f"/api/key/{api_key_id}", json=key_data)

    def delete_api_key(self, api_key_id):
        """Delete an API key.

        DELETE /api/key/{apiKeyId}
        """
        return self.client._request("DELETE", f"/api/key/{api_key_id}")

    # ---- Advanced API Keys ----
    def get_advanced_api_key(self, api_key_id):
        """Get details of an advanced API key.

        GET /api/key/{apiKeyId}/advanced
        """
        return self.client._request("GET", f"/api/key/{api_key_id}/advanced")

    def update_advanced_api_key(self, api_key_id, key_data):
        """Update an advanced API key.

        POST /api/key/{apiKeyId}/advanced
        """
        return self.client._request("POST", f"/api/key/{api_key_id}/advanced", json=key_data)

    def create_advanced_api_key(self, api_key_id, key_data):
        """Create an advanced API key.

        PUT /api/key/{apiKeyId}/advanced
        """
        return self.client._request("PUT", f"/api/key/{api_key_id}/advanced", json=key_data)

    def delete_advanced_api_key(self, api_key_id):
        """Delete an advanced API key.

        DELETE /api/key/{apiKeyId}/advanced
        """
        return self.client._request("DELETE", f"/api/key/{api_key_id}/advanced")

    def reactivate_advanced_api_key(self, api_key_id):
        """Reactivate a deactivated advanced API key.

        POST /api/key/{apiKeyId}/advanced/reactivate
        """
        return self.client._request("POST", f"/api/key/{api_key_id}/advanced/reactivate")

    # ---- API Key Tokens ----
    def list_api_key_tokens(self, api_key_id):
        """List all tokens for a given API key.

        GET /api/key/{apiKeyId}/token
        """
        return self.client._request("GET", f"/api/key/{api_key_id}/token")

    def create_api_key_token(self, api_key_id, token_data):
        """Create a token for a given API key.

        PUT /api/key/{apiKeyId}/token
        """
        return self.client._request("PUT", f"/api/key/{api_key_id}/token", json=token_data)

    def update_api_key_token(self, api_key_id, token_id, token_data):
        """Update an API key token.

        POST /api/key/{apiKeyId}/token/{id}
        """
        return self.client._request("POST", f"/api/key/{api_key_id}/token/{token_id}", json=token_data)

    def delete_api_key_token(self, api_key_id, token_id):
        """Delete an API key token.

        DELETE /api/key/{apiKeyId}/token/{id}
        """
        return self.client._request("DELETE", f"/api/key/{api_key_id}/token/{token_id}")
