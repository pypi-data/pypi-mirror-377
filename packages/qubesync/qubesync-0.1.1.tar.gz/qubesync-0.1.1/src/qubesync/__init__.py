"""
QubeSync - Python library for QuickBooks integration via QubeSync API

This package provides:
- QubeSync: Main API client for interacting with QubeSync service
- RequestBuilder: DSL for building QuickBooks XML requests
- Exception classes for error handling

Usage:
    from qubesync import QubeSync, RequestBuilder
    
    # API operations
    connection = QubeSync.create_connection(options)
    
    # Request building
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            # ... build request
"""

# Import main classes for convenient access
from .client import (
    QubeSync,
    QubeSyncError,
    StaleWebhookError, 
    InvalidWebhookSignatureError,
    ConfigError
)

from .request_builder import (
    RequestBuilder,
    RequestElement,
    FluentRequestBuilder
)

# Version info
__version__ = "0.1.0"

# Public API
__all__ = [
    # Main API client
    "QubeSync",
    
    # Request builders
    "RequestBuilder", 
    "RequestElement",
    "FluentRequestBuilder",
    
    # Exceptions
    "QubeSyncError",
    "StaleWebhookError",
    "InvalidWebhookSignatureError", 
    "ConfigError",
    
    # Version
    "__version__"
]
