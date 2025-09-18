# HoodPay Python SDK

Lightweight Python SDK for the HoodPay API (customers, payments).

## Installation

```bash
pip install hoodpay-py
```

or

```bash
poetry add hoodpay-py
```

## Setup

Before using the SDK, you'll need to obtain your Business ID and generate an API key from your HoodPay account.

1. Log in to your [HoodPay account](https://dash.hoodpay.io)
2. Navigate to [Settings > Developer](https://dash.hoodpay.io/settings/developer)
3. Copy your Business ID and generate a new API key, then copy it securely

**⚠️ Important:** Keep your API key secure and never commit it to version control.

## Usage

```python
from hoodpay_py import HoodPayClient

client = HoodPayClient(
    api_key='your-api-key-here',
    business_id='your-business-id-here'
)

# Create a payment
request = CreatePaymentRequest(
    amount=5.0,
    currency='USD',
    name='Subscription Test'
)
payment_response = client.payments.create(request)

print(payment)

# List payments with pagination
payments = client.payments.list(
    search_string='test',
    page_size=10,
    page_number=1
)

print(payments)

# Get a single payment
single_payment = client.payments.get('payment-id')
print(single_payment)

# List customers
customers = client.customers.list(
    search_string='email@example.com',
    page_size=10,
    page_number=1
)

print(customers)

# Get a single customer
customer = client.customers.get(123)
print(customer)

# Search for customers and payments
search_results = client.search('alice')
print(search_results)

# Select payment method (public endpoint, no auth required)
select_result = client.livePayments.select_payment_method('payment-id', 'ETHEREUM')
print(select_result)

# Fill customer email (public endpoint)
email_result = client.livePayments.fill_customer_email(
    'payment-id',
    'customer@example.com'
)
print(email_result)

# Cancel payment (public endpoint)
cancel_result = client.livePayments.cancel_payment('payment-id')
print(cancel_result)
```

## API Reference

### HoodPayClient

Main client class for interacting with the HoodPay API.

#### Constructor Options

- `api_key` (str): Your HoodPay API key
- `business_id` (str): Your business ID

### Payments

#### create(data: CreatePaymentRequest): Dict[str, Any]

Creates a new payment.

Parameters:

- `data`: Payment creation data
  - `paymentMethods` (optional): Object specifying allowed payment methods. If not provided, all available payment methods will be used.

#### list(search_string: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> Dict[str, Any]

Lists payments with optional search and pagination.

Parameters:

- `search_string`: Search string for filtering
- `page_size`: Number of payments per page
- `page_number`: Page number

#### get(payment_id: str): PaymentResponse

Gets a single payment by ID.

Parameters:

- `payment_id`: Payment ID

### Customers

#### list(search_string: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> Dict[str, Any]

Lists customers with optional search and pagination.

Parameters:

- `search_string`: Search string for filtering
- `page_size`: Number of customers per page
- `page_number`: Page number

#### get(customer_id: int): Dict[str, Any]

Gets a single customer by ID.

Parameters:

- `customer_id`: Customer ID

### search(query: str): Dict[str, Any]

Searches for customers and payments matching the provided query string.

Parameters:

- `query`: Search query string

Returns a `SearchResult` containing matching customers and payments.

### Live Payments

#### selectPaymentMethod(payment_id: str, crypto: CryptoCode) -> Dict[str, Any]

Selects a payment method for a hosted payment page. Automatically detects whether to use XPUB (for LITECOIN/BITCOIN) or direct crypto submission.

Parameters:

- `payment_id`: Payment ID from the hosted page
- `crypto`: CryptoCode literal

Returns a `SelectPaymentMethodResponse` with charge details.

#### fill_customer_email(payment_id: str, email: str) -> Dict[str, Any]

Fills the customer email for a hosted payment page.

Parameters:

- `payment_id`: Payment ID from the hosted page
- `email`: Customer email address

Returns: Dict with 'message': str

#### cancel_payment(payment_id: str) -> Dict[str, Any]

Cancels a payment on the hosted page.

Parameters:

- `payment_id`: Payment ID from the hosted page

Returns: Dict with 'message': str

## Types

### CreatePaymentRequest

- `description?: str` - Optional description of the payment
- `amount: float` - The amount of the payment
- `currency: str` - The currency code for the payment (ISO 4217 format, e.g. USD)
- `name: str` - The name associated with the payment
- `redirectUrl?: str` - Optional URL to redirect after payment
- `notifyUrl?: str` - Optional URL for payment notifications
- `customerEmail?: str` - Optional email of the customer
- `customerIp?: str | None` - Optional IP address of the customer
- `customerUserAgent?: str | None` - Optional user agent of the customer

### Payment

- `id: str` - Payment ID
- `name?: str` - Optional name
- `description?: str` - Optional description
- `endAmount: float` - Payment amount
- `prePaymentAmount?: float` - Pre-payment amount
- `currency: str` - Currency code
- `status: str` - Payment status
- `createdAt: str` - Creation timestamp
- `expiresAt?: str` - Optional expiration timestamp
- `timeline?: TimelineEntry[]` - Optional status timeline
- `customer?: Customer` - Optional customer info
- `paymentMethod?: str` - Optional payment method
- `selectedPaymentMethod?: str` - Optional selected payment method
- `directCryptoCharge?: HoodPayCryptoCharge` - Optional crypto charge details
- `hoodPayFee?: float` - Optional fee
- `onBehalfOfBusinessId?: int` - Optional business ID
- `netAmountUsd?: float` - Optional net amount in USD
- `customerEmail?: str` - Optional customer email

### CustomerStat

- `id: int` - Customer ID
- `email: str` - Customer email
- `totalPayments: int` - Total payments
- `totalSpend: float` - Total spend
- `firstSeen: str` - First seen timestamp
- `lastPayment?: str` - Optional last payment timestamp

### SearchResult

- `customers: SearchCustomer[]` - Matching customers
- `payments: Payment[]` - Matching payments

### SelectPaymentMethodResponse

- `data.chargeId: str` - Charge ID
- `data.chargeCryptoAmount: str` - Crypto amount to pay
- `data.chargeCryptoName: str` - Crypto name
- `data.chargeCryptoAddress: str` - Crypto address to send to
- `message: str` - Response message

## Supported Crypto Codes

The following crypto codes are supported:

- BITCOIN
- ETHEREUM
- LITECOIN
- BITCOIN_CASH
- ETH_USD_COIN
- ETH_TETHER
- ETH_BNB
- ETH_BUSD
- ETH_MATIC
- ETH_SHIBA_INU
- ETH_APE_COIN
- ETH_CRONOS
- ETH_DAI
- ETH_UNISWAP

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Lint
poetry run ruff check src/

# Format
poetry run ruff format src/

# Type check
poetry run mypy src/

# Build
poetry build
```

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## License

MIT
