class AccountUser:
    """Sub-client for managing account users."""

    def __init__(self, client):
        self.client = client

    def list_account_users(self):
        return self.client._request("GET", "/account/user")

    def create_account_user(self, user_data):
        return self.client._request("PUT", "/account/user", json=user_data)

    def get_account_user(self, account_user_id):
        return self.client._request("GET", f"/account/user/{account_user_id}")

    def update_account_user(self, account_user_id, user_data):
        return self.client._request("POST", f"/account/user/{account_user_id}", json=user_data)

    def delete_account_user(self, account_user_id):
        return self.client._request("DELETE", f"/account/user/{account_user_id}")