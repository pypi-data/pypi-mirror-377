from __future__ import annotations
from typing import Dict, Any
from ..types import CryptoCode


class LivePayments:
    def __init__(self: "LivePayments", client: Any):
        self.client = client

    def select_payment_method(self, payment_id: str, crypto: CryptoCode) -> Dict[str, Any]:
        if crypto in ["BITCOIN", "LITECOIN"]:
            data = {"xPub_Crypto": crypto, "onRamp_Crypto": None}
        else:
            data = {"direct_Crypto": crypto}
        response = self.client._request(
            "POST",
            f"/v1/public/payments/hosted-page/{payment_id}/select-payment-method",
            data=data,
            auth_required=False,
        )
        return response

    def fill_customer_email(self, payment_id: str, email: str) -> Dict[str, Any]:
        data = {"email": email}
        return self.client._request(
            "POST", f"/v1/public/payments/hosted-page/{payment_id}/customer_email", data=data, auth_required=False
        )

    def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        return self.client._request("POST", f"/v1/public/payments/hosted-page/{payment_id}/cancel", auth_required=False)
