class AddressReservation:
    """Sub-client for managing address reservations."""

    def __init__(self, client):
        self.client = client

    def list_reservations(self, address_id):
        """Get a list of address reservations for a specific address.

        GET /address/{addressId}/reservation
        """
        return self.client._request("GET", f"/address/{address_id}/reservation")

    def issue_reservation(self, address_id, reservation_id):
        """Issue authorizations for an address reservation.

        POST /address/{addressId}/reservation/{reservationId}/issue
        """
        return self.client._request("POST", f"/address/{address_id}/reservation/{reservation_id}/issue")

    def revoke_reservation(self, address_id, reservation_id):
        """Revoke authorizations for an address reservation.

        POST /address/{addressId}/reservation/{reservationId}/revoke
        """
        return self.client._request("POST", f"/address/{address_id}/reservation/{reservation_id}/revoke")

    def update_reservation_access_times(self, address_id, reservation_id, access_times):
        """Update access times of a reservation.

        POST /address/{addressId}/reservation/{reservationId}/update/accesstimes
        """
        return self.client._request(
            "POST",
            f"/address/{address_id}/reservation/{reservation_id}/update/accesstimes",
            json=access_times,
        )
