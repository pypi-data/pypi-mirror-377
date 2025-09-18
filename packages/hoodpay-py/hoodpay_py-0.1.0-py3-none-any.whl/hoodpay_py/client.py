from __future__ import annotations
import requests
from typing import Optional, Dict, Any, cast
from .exceptions import HoodPayAPIError, HoodPayAuthError
from .resources.payments import Payments
from .resources.customers import Customers
from .resources.live_payments import LivePayments


class HoodPayClient:
    def __init__(self, api_key: str, business_id: str):
        self.api_key = api_key
        self.business_id = business_id
        self.base_url = "https://api.hoodpay.io"
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        self.public_session = requests.Session()
        self.public_session.headers.update(
            {"Content-Type": "application/json"})
        self.payments = Payments(self, business_id)
        self.customers = Customers(self, business_id)
        self.livePayments = LivePayments(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        session = self.session if auth_required else self.public_session
        response = None
        try:
            response = session.request(method, url, json=data, params=params)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except requests.exceptions.HTTPError as e:
            if response and response.status_code == 401:
                raise HoodPayAuthError("Authentication failed") from e
            raise HoodPayAPIError(
                f"API error: {response.text if response else str(e)}", response.status_code if response else None
            ) from e
        except requests.exceptions.RequestException as e:
            raise HoodPayAPIError(f"Request failed: {str(e)}") from e

    def search(self, query: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/dash/businesses/{self.business_id}/search", params={"data": query})
