class ApiKey:
    """Sub-client for managing API keys, advanced keys, and tokens."""

    def __init__(self, client):
        self.client = client

    # ---- API Keys ----
    def list_api_keys(self):
        return self.client._request("GET", "/api/key")

    def create_api_key(self, key_data):
        return self.client._request("PUT", "/api/key", json=key_data)

    def update_api_key(self, api_key_id, key_data):
        return self.client._request("POST", f"/api/key/{api_key_id}", json=key_data)

    def delete_api_key(self, api_key_id):
        return self.client._request("DELETE", f"/api/key/{api_key_id}")

    # ---- Advanced API Keys ----
    def get_advanced_api_key(self, api_key_id):
        return self.client._request("GET", f"/api/key/{api_key_id}/advanced")

    def update_advanced_api_key(self, api_key_id, key_data):
        return self.client._request("POST", f"/api/key/{api_key_id}/advanced", json=key_data)

    def create_advanced_api_key(self, api_key_id, key_data):
        return self.client._request("PUT", f"/api/key/{api_key_id}/advanced", json=key_data)

    def delete_advanced_api_key(self, api_key_id):
        return self.client._request("DELETE", f"/api/key/{api_key_id}/advanced")

    def reactivate_advanced_api_key(self, api_key_id):
        return self.client._request("POST", f"/api/key/{api_key_id}/advanced/reactivate")

    # ---- API Key Tokens ----
    def list_api_key_tokens(self, api_key_id):
        return self.client._request("GET", f"/api/key/{api_key_id}/token")

    def create_api_key_token(self, api_key_id, token_data):
        return self.client._request("PUT", f"/api/key/{api_key_id}/token", json=token_data)

    def update_api_key_token(self, api_key_id, token_id, token_data):
        return self.client._request("POST", f"/api/key/{api_key_id}/token/{token_id}", json=token_data)

    def delete_api_key_token(self, api_key_id, token_id):
        return self.client._request("DELETE", f"/api/key/{api_key_id}/token/{token_id}")