from __future__ import annotations
from typing import Optional, Dict, Any


class Customers:
    def __init__(self: "Customers", client: Any, business_id: str):
        self.client = client
        self.business_id = business_id

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
            "GET", f"/v1/dash/businesses/{self.business_id}/customers", params=params)
        return response

    def get(self, customer_id: int) -> Dict[str, Any]:
        return self.client._request("GET", f"/v1/dash/businesses/{self.business_id}/customers/{customer_id}")
