class Address:
    """Sub-client for managing addresses and address units."""

    def __init__(self, client):
        self.client = client

    # ---- Address CRUD ----
    def list_addresses(self):
        """List all addresses.

        GET /address
        """
        return self.client._request("GET", "/address")

    def create_address(self, address_data):
        """Create a new address.

        PUT /address
        """
        return self.client._request("PUT", "/address", json=address_data)

    def update_address(self, address_id, address_data):
        """Update an existing address.

        POST /address/{addressId}
        """
        return self.client._request("POST", f"/address/{address_id}", json=address_data)

    def delete_address(self, address_id):
        """Delete an existing address.

        DELETE /address/{addressId}
        """
        return self.client._request("DELETE", f"/address/{address_id}")

    # ---- Address Units ----
    def list_address_units(self, address_id):
        """List all address units for a given address.

        GET /address/{addressId}/unit
        """
        return self.client._request("GET", f"/address/{address_id}/unit")

    def create_address_unit(self, address_id, unit_data):
        """Create a new unit for a given address.

        PUT /address/{addressId}/unit
        """
        return self.client._request("PUT", f"/address/{address_id}/unit", json=unit_data)

    def delete_address_units(self, address_id):
        """Delete all units of a given address.

        DELETE /address/{addressId}/unit
        """
        return self.client._request("DELETE", f"/address/{address_id}/unit")

    def delete_address_unit(self, address_id, unit_id):
        """Delete a specific unit of a given address.

        DELETE /address/{addressId}/unit/{unitId}
        """
        return self.client._request("DELETE", f"/address/{address_id}/unit/{unit_id}")
