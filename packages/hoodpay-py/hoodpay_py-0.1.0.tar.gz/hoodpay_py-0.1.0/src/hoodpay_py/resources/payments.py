from __future__ import annotations
from typing import Dict, Any, Optional
from ..types import CreatePaymentRequest


class Payments:
    def __init__(self: "Payments", client: Any, business_id: str):
        self.client = client
        self.business_id = business_id

    def create(self, data: CreatePaymentRequest) -> Dict[str, Any]:
        return self.client._request("POST", f"/v1/businesses/{self.business_id}/payments", data=data.__dict__)

    def list(
        self, search_string: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        params = {}
        if search_string:
            params["searchString"] = search_string
        if page_size:
            params["PageSize"] = str(page_size)
        if page_number:
            params["PageNumber"] = str(page_number)
        response = self.client._request(
            "GET", f"/v1/businesses/{self.business_id}/payments", params=params)
        return response

    def get(self, payment_id: str) -> Dict[str, Any]:
        response = self.client._request(
            "GET", f"/v1/businesses/{self.business_id}/payments/{payment_id}")
        return response
