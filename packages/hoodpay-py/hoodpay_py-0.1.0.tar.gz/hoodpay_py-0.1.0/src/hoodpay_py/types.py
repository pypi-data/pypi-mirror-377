from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from typing_extensions import Literal


@dataclass
class CreatePaymentRequest:
    amount: float
    currency: str
    name: str
    description: Optional[str] = None
    redirectUrl: Optional[str] = None
    notifyUrl: Optional[str] = None
    customerEmail: Optional[str] = None
    customerIp: Optional[str] = None
    customerUserAgent: Optional[str] = None
    paymentMethods: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CreatePaymentResponseData:
    url: str
    id: str


@dataclass
class CreatePaymentResponse:
    data: CreatePaymentResponseData
    message: str


@dataclass
class HoodPayCryptoCharge:
    amount: float
    coinName: str
    exchangeRate: Optional[float] = None
    isUnderpaid: Optional[bool] = None
    address: Optional[str] = None
    walletName: Optional[str] = None


@dataclass
class Customer:
    id: int
    email: str


@dataclass
class TimelineEntry:
    time: str
    paymentStatus: str


@dataclass
class Payment:
    id: str
    endAmount: float
    currency: str
    status: str
    createdAt: str
    name: Optional[str] = None
    description: Optional[str] = None
    prePaymentAmount: Optional[float] = None
    expiresAt: Optional[str] = None
    timeline: Optional[List[TimelineEntry]] = None
    customer: Optional[Customer] = None
    paymentMethod: Optional[str] = None
    selectedPaymentMethod: Optional[str] = None
    directCryptoCharge: Optional[HoodPayCryptoCharge] = None
    hoodPayFee: Optional[float] = None
    onBehalfOfBusinessId: Optional[int] = None
    netAmountUsd: Optional[float] = None
    customerEmail: Optional[str] = None


@dataclass
class IpAddress:
    city: str
    ip: str
    country: str
    riskScore: float
    connectionType: str
    isp: str


@dataclass
class CustomerStat:
    id: int
    email: str
    totalPayments: int
    totalSpend: float
    firstSeen: str
    lastPayment: Optional[str] = None
    ipAddresses: Optional[List[IpAddress]] = None


@dataclass
class SearchCustomer:
    id: int
    email: str
    createdAt: str


@dataclass
class SearchResult:
    customers: List[SearchCustomer]
    payments: List[Payment]


@dataclass
class PaymentListResponse:
    data: List[Payment]
    message: str


@dataclass
class CustomerListResponse:
    data: List[CustomerStat]
    message: str


@dataclass
class PaymentResponse:
    data: Payment


@dataclass
class CustomerResponse:
    data: CustomerStat
    message: str


@dataclass
class SearchResponse:
    data: SearchResult
    message: str


@dataclass
class SelectPaymentMethodResponseData:
    chargeId: str
    chargeCryptoAmount: str
    chargeCryptoName: str
    chargeCryptoAddress: str


@dataclass
class SelectPaymentMethodResponse:
    data: SelectPaymentMethodResponseData
    message: str


@dataclass
class FillCustomerEmailResponse:
    message: str


@dataclass
class CancelPaymentResponse:
    message: str


CryptoCode = Literal[
    "BITCOIN",
    "ETHEREUM",
    "LITECOIN",
    "BITCOIN_CASH",
    "ETH_USD_COIN",
    "ETH_TETHER",
    "ETH_BNB",
    "ETH_BUSD",
    "ETH_MATIC",
    "ETH_SHIBA_INU",
    "ETH_APE_COIN",
    "ETH_CRONOS",
    "ETH_DAI",
    "ETH_UNISWAP",
]
