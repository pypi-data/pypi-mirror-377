from typing import Any, Dict


class Account:
    """Sub-client for managing account-level operations and settings."""

    def __init__(self, client):
        self.client = client  # reference to the parent NukiClient

    # ---- Account CRUD ----
    def get(self) -> Dict[str, Any]:
        """Get account details.

        GET /account
        """
        return self.client._request("GET", "/account")

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update account details.

        POST /account
        """
        return self.client._request("POST", "/account", json=data)

    def delete(self) -> Dict[str, Any]:
        """Delete the account.

        DELETE /account
        """
        return self.client._request("DELETE", "/account")

    # ---- Email ----
    def change_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Change account email.

        POST /account/email/change
        """
        return self.client._request("POST", "/account/email/change", json=data)

    def verify_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify account email.

        POST /account/email/verify
        """
        return self.client._request("POST", "/account/email/verify", json=data)

    # ---- Integrations ----
    def list_integrations(self) -> Dict[str, Any]:
        """List all account integrations.

        GET /account/integration
        """
        return self.client._request("GET", "/account/integration")

    def delete_integration(self, integration_id: str) -> Dict[str, Any]:
        """Delete a specific account integration.

        DELETE /account/integration
        """
        return self.client._request("DELETE", "/account/integration", json={"id": integration_id})

    # ---- OTP ----
    def enable_otp(self) -> Dict[str, Any]:
        """Enable OTP for the account.

        POST /account/otp
        """
        return self.client._request("POST", "/account/otp")

    def create_otp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an OTP.

        PUT /account/otp
        """
        return self.client._request("PUT", "/account/otp", json=data)

    def disable_otp(self) -> Dict[str, Any]:
        """Disable OTP for the account.

        DELETE /account/otp
        """
        return self.client._request("DELETE", "/account/otp")

    # ---- Password ----
    def reset_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reset account password.

        POST /account/password/reset
        """
        return self.client._request("POST", "/account/password/reset", json=data)

    # ---- Account Settings ----
    def get_setting(self) -> Dict[str, Any]:
        """Get account settings.

        GET /account/setting
        """
        return self.client._request("GET", "/account/setting")

    def update_setting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update account settings.

        PUT /account/setting
        """
        return self.client._request("PUT", "/account/setting", json=data)

    def delete_setting(self, key: str) -> Dict[str, Any]:
        """Delete a specific account setting.

        DELETE /account/setting
        """
        return self.client._request("DELETE", "/account/setting", json={"key": key})

    # ---- Sub-Accounts ----
    def list_sub_accounts(self) -> Dict[str, Any]:
        """List all sub-accounts.

        GET /account/sub
        """
        return self.client._request("GET", "/account/sub")

    def create_sub_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sub-account.

        PUT /account/sub
        """
        return self.client._request("PUT", "/account/sub", json=data)

    def get_sub_account(self, account_id: str) -> Dict[str, Any]:
        """Get details of a specific sub-account.

        GET /account/sub/{accountId}
        """
        return self.client._request("GET", f"/account/sub/{account_id}")

    def update_sub_account(self, account_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific sub-account.

        POST /account/sub/{accountId}
        """
        return self.client._request("POST", f"/account/sub/{account_id}", json=data)

    def delete_sub_account(self, account_id: str) -> Dict[str, Any]:
        """Delete a specific sub-account.

        DELETE /account/sub/{accountId}
        """
        return self.client._request("DELETE", f"/account/sub/{account_id}")
