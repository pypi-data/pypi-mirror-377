# ---------------------------
# Account sub-class
# ---------------------------
from typing import Any, Dict

class Account:
    def __init__(self, client):
        self.client = client  # reference to the parent NukiClient

    # GET /account
    def get(self) -> Dict[str, Any]:
        return self.client._request("GET", "/account")

    # POST /account
    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", "/account", json=data)

    # DELETE /account
    def delete(self) -> Dict[str, Any]:
        return self.client._request("DELETE", "/account")

    # POST /account/email/change
    def change_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", "/account/email/change", json=data)

    # POST /account/email/verify
    def verify_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", "/account/email/verify", json=data)

    # GET /account/integration
    def list_integrations(self) -> Dict[str, Any]:
        return self.client._request("GET", "/account/integration")

    # DELETE /account/integration
    def delete_integration(self, integration_id: str) -> Dict[str, Any]:
        return self.client._request("DELETE", "/account/integration", json={"id": integration_id})

    # POST /account/otp
    def enable_otp(self) -> Dict[str, Any]:
        return self.client._request("POST", "/account/otp")

    # PUT /account/otp
    def create_otp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("PUT", "/account/otp", json=data)

    # DELETE /account/otp
    def disable_otp(self) -> Dict[str, Any]:
        return self.client._request("DELETE", "/account/otp")

    # POST /account/password/reset
    def reset_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", "/account/password/reset", json=data)

    # GET /account/setting
    def get_setting(self) -> Dict[str, Any]:
        return self.client._request("GET", "/account/setting")

    # PUT /account/setting
    def update_setting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("PUT", "/account/setting", json=data)

    # DELETE /account/setting
    def delete_setting(self, key: str) -> Dict[str, Any]:
        return self.client._request("DELETE", "/account/setting", json={"key": key})

    # GET /account/sub
    def list_sub_accounts(self) -> Dict[str, Any]:
        return self.client._request("GET", "/account/sub")

    # PUT /account/sub
    def create_sub_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("PUT", "/account/sub", json=data)

    # GET /account/sub/{accountId}
    def get_sub_account(self, account_id: str) -> Dict[str, Any]:
        return self.client._request("GET", f"/account/sub/{account_id}")

    # POST /account/sub/{accountId}
    def update_sub_account(self, account_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request("POST", f"/account/sub/{account_id}", json=data)

    # DELETE /account/sub/{accountId}
    def delete_sub_account(self, account_id: str) -> Dict[str, Any]:
        return self.client._request("DELETE", f"/account/sub/{account_id}")