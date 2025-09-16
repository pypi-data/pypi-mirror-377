# QubeSync Python Library

A Python library for seamless QuickBooks integration via the QubeSync API. This library provides both a robust API client for QubeSync operations and a powerful DSL (Domain Specific Language) for building QuickBooks XML requests.

## Features

- 🔌 **Complete QubeSync API client** - Connect, queue requests, handle webhooks
- 🏗️ **Intuitive Request Builder DSL** - Build QBXML requests with Python syntax
- 🔒 **Webhook security** - Built-in signature verification for webhooks
- 🚀 **Multiple syntax styles** - Context managers, fluent chaining, or Ruby-like syntax
- ✅ **Fully tested** - comprehensive tests ensuring reliability
- 📦 **Clean imports** - Simple `from qubesync import ...` syntax

## Installation

```bash
pip install qubesync
```

Or install from source:

```bash
git clone https://github.com/qubeintegrations/qube_sync_py
cd qube_sync_py
pip install -e .
```

## Quick Start

### Environment Setup

Set your QubeSync credentials:

```bash
export QUBE_API_KEY="your_api_key_here"
export QUBE_WEBHOOK_SECRET="your_webhook_secret_here"
export QUBE_URL="https://qubesync.com/api/v1"  # Optional, defaults to this
```

### Basic Usage

```python
from qubesync import QubeSync, RequestBuilder

# 1. Create a connection
connection = QubeSync.create_connection({
    "name": "My Customer Inc.", # optional (will populate from QuickBooks on first sync if blank)
    "redirect_url": "https://your-app.com/qbd-setup/callback"
})

# 2. Build a request using the DSL
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.CustomerQueryRq(requestID='customer_123', iterator='Start') as query:
                query.MaxReturned(50)
                query.IncludeRetElement('ListID')
                query.IncludeRetElement('Name')
                query.IncludeRetElement('Email')

# 3. Queue the request
response = QubeSync.queue_request(connection['id'], {
    'request_json': request.as_json(),
    'webhook_url': 'https://your-app.com/webhooks/qb_response'
})

print(f"Request queued with ID: {response['id']}")
```

## API Client Reference

### Connection Management

```python
from qubesync import QubeSync

# Create a new connection
connection = QubeSync.create_connection({
    "name": "My Customer Inc.", # optional (will populate from QuickBooks on first sync if blank)
    "redirect_url": "https://your-app.com/qbd-setup/callback"
})

# Get connection details
connection = QubeSync.get_connection(connection_id)

# Delete a connection
QubeSync.delete_connection(connection_id)

# Generate QWC file for QuickBooks
qwc_content = QubeSync.get_qwc(connection_id)

# Generate password for QuickBooks connection
password = QubeSync.generate_password(connection_id)
```

### Request Management

```python
# Queue a request
request_data = {
    'request_json': {...},  # Built using RequestBuilder
    'webhook_url': 'https://your-app.com/webhook'
}
response = QubeSync.queue_request(connection_id, request_data)

# Get request status
request = QubeSync.get_request(request_id)

# Get all requests for a connection
requests = QubeSync.get_requests(connection_id)

# Delete a request
QubeSync.delete_request(request_id)
```

### Webhook Handling

```python
# Verify and parse webhook payload
def handle_webhook(request):
    signature = request.headers.get('X-Qube-Signature')
    body = request.body.decode('utf-8')
    
    try:
        webhook_data = QubeSync.verify_and_build_webhook(body, signature)
        # Process the verified webhook data in the background
        # to ensure a quick response
        print(f"Received response for request: {webhook_data['request_id']}")
        return {"status": "success"}
    except (StaleWebhookError, InvalidWebhookSignatureError) as e:
        print(f"Webhook verification failed: {e}")
        return {"status": "error"}, 400
```

## RequestBuilder DSL

The RequestBuilder provides an intuitive Python DSL for constructing QBXML requests that get converted to JSON format for the QubeSync API.

### Context Manager Style (Recommended)

```python
from qubesync import RequestBuilder

request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.InvoiceQueryRq(requestID='inv_query_123') as query:
                query.MaxReturned(25)
                query.IncludeRetElement('TxnID')
                query.IncludeRetElement('TxnNumber')
                query.IncludeRetElement('CustomerRef')
                query.IncludeRetElement('TxnDate')
                query.IncludeRetElement('DueDate')
                query.IncludeRetElement('BalanceRemaining')

json_data = request.as_json()
```

### Fluent Chaining Style

```python
from qubesync import FluentRequestBuilder

request = FluentRequestBuilder(version="16.0")
request.QBXML().QBXMLMsgsRq(onError='stopOnError').ItemQueryRq(
    requestID='item_query_456'
).add_children([
    ('MaxReturned', 100),
    ('IncludeRetElement', 'ListID'),
    ('IncludeRetElement', 'Name'),
    ('IncludeRetElement', 'Type'),
    ('IncludeRetElement', 'SalePrice')
])

json_data = request.as_json()
```

### Ruby-like Style

```python
from qubesync import RequestBuilder

request = RequestBuilder(version="16.0")
qbxml = request.QBXML()
msgs = qbxml.QBXMLMsgsRq(onError='stopOnError')
query = msgs.CustomerQueryRq(requestID='customer_789', iterator='Start')
query.MaxReturned(30)
query.IncludeRetElement('ListID')
query.IncludeRetElement('Name')
query.IncludeRetElement('CompanyName')

json_data = request.as_json()
```

### Handling Python Reserved Words

Use trailing underscores for Python reserved words:

```python
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            # Use trailing underscore for 'class', 'for', 'if', etc.
            with msgs.CustomQueryRq(class_='invoice', for_='reports') as query:
                query.MaxReturned(100)
```

### Complex Nested Structures

```python
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.InvoiceAddRq(requestID='invoice_add_999') as add_req:
                with add_req.InvoiceAdd() as invoice:
                    with invoice.CustomerRef() as customer_ref:
                        customer_ref.ListID('80000001-1234567890')
                    
                    invoice.TxnDate('2024-01-15')
                    invoice.RefNumber('INV-2024-001')
                    
                    with invoice.InvoiceLineAdd() as line:
                        with line.ItemRef() as item_ref:
                            item_ref.ListID('80000002-1234567890')
                        line.Desc('Professional Services')
                        line.Quantity(10)
                        line.Rate(150.00)
```

## Example Output

The RequestBuilder generates clean JSON that the QubeSync API processes:

```json
{
  "version": "16.0",
  "request": [
    {
      "name": "QBXML",
      "children": [
        {
          "name": "QBXMLMsgsRq",
          "attributes": {"onError": "stopOnError"},
          "children": [
            {
              "name": "CustomerQueryRq",
              "attributes": {"requestID": "customer_123", "iterator": "Start"},
              "children": [
                {"name": "MaxReturned", "text": 50},
                {"name": "IncludeRetElement", "text": "ListID"},
                {"name": "IncludeRetElement", "text": "Name"},
                {"name": "IncludeRetElement", "text": "Email"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Error Handling

```python
from qubesync import (
    QubeSync, 
    QubeSyncError, 
    ConfigError, 
    StaleWebhookError, 
    InvalidWebhookSignatureError
)

try:
    connection = QubeSync.create_connection({"name": "Test"})
except ConfigError as e:
    print(f"Configuration error: {e}")
except QubeSyncError as e:
    print(f"API error: {e}")

# Webhook verification
try:
    webhook_data = QubeSync.verify_and_build_webhook(body, signature)
except StaleWebhookError:
    print("Webhook is too old")
except InvalidWebhookSignatureError:
    print("Invalid webhook signature")
```

## Available Classes

### API Client
- `QubeSync` - Main API client for all QubeSync operations
- `QubeSyncError` - Base exception class
- `ConfigError` - Configuration/environment variable errors
- `StaleWebhookError` - Webhook timestamp too old
- `InvalidWebhookSignatureError` - Webhook signature verification failed

### Request Building
- `RequestBuilder` - Context manager style DSL (recommended)
- `FluentRequestBuilder` - Method chaining style DSL
- `RequestElement` - Individual request element (advanced usage)

## Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run specific test file
python run_tests.py tests/test_request_builder.py
```

### Running Examples

```bash
# Run all examples
python examples.py

# Use virtual environment
./bin/python examples.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📧 Email: support@qubesync.com
- 📖 Documentation: [QubeSync Docs](https://docs.qubesync.com)
- 🐛 Issues: [GitHub Issues](https://github.com/qubeintegrations/qube_sync_py/issues)

## Changelog

### v0.1.0
- Initial release
- Complete QubeSync API client
- RequestBuilder DSL with multiple syntax styles
- Comprehensive test suite
- Webhook security verification
- Clean module structure with intuitive imports
