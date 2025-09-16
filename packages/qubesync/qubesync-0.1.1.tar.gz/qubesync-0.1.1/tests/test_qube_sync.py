import pytest
import os
import time
import json
import hmac
import hashlib
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from qubesync import QubeSync, QubeSyncError, ConfigError, StaleWebhookError, InvalidWebhookSignatureError

# Set up test environment variables
os.environ["QUBE_API_KEY"] = "test_api_key"
os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"

class TestQubeSync:
    
    def setup_method(self):
        """Setup method run before each test"""
        # Ensure environment variables are set
        os.environ["QUBE_API_KEY"] = "test_api_key"
        os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"
    
    def test_base_url_default(self):
        """Test base_url returns default when QUBE_URL not set"""
        if "QUBE_URL" in os.environ:
            del os.environ["QUBE_URL"]
        assert QubeSync.base_url() == "https://qubesync.com/api/v1"
    
    def test_base_url_custom(self):
        """Test base_url returns custom URL when QUBE_URL is set"""
        os.environ["QUBE_URL"] = "https://custom.api.com"
        assert QubeSync.base_url() == "https://custom.api.com"
        # Clean up
        del os.environ["QUBE_URL"]
    
    def test_default_headers(self):
        """Test default headers are correct"""
        headers = QubeSync.default_headers()
        expected = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        assert headers == expected
    
    def test_api_key_success(self):
        """Test api_key returns the correct key when set"""
        assert QubeSync.api_key() == "test_api_key"
    
    def test_api_key_missing(self):
        """Test api_key raises ConfigError when not set"""
        del os.environ["QUBE_API_KEY"]
        with pytest.raises(ConfigError, match="QUBE_API_KEY not set in environment"):
            QubeSync.api_key()
        # Restore for other tests
        os.environ["QUBE_API_KEY"] = "test_api_key"
    
    def test_api_secret_success(self):
        """Test api_secret returns the correct secret when set"""
        assert QubeSync.api_secret() == "supersecret"
    
    def test_api_secret_missing(self):
        """Test api_secret raises ConfigError when not set"""
        del os.environ["QUBE_WEBHOOK_SECRET"]
        with pytest.raises(ConfigError, match="QUBE_WEBHOOK_SECRET not set in environment"):
            QubeSync.api_secret()
        # Restore for other tests
        os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"
    
    @patch('requests.Session')
    def test_conn(self, mock_session):
        """Test conn creates a session with proper auth"""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        result = QubeSync.conn()
        
        mock_session.assert_called_once()
        assert mock_session_instance.auth == ("test_api_key", "")
        assert result == mock_session_instance
    
    @patch.object(QubeSync, 'conn')
    def test_get_success(self, mock_connection):
        """Test GET request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_connection.return_value = mock_session
        
        result = QubeSync.get("test/endpoint")
        
        mock_session.get.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers()
        )
        assert result == {"data": "test"}
    
    @patch.object(QubeSync, 'conn')
    def test_get_error(self, mock_connection):
        """Test GET request error handling"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_session.get.return_value = mock_response
        mock_connection.return_value = mock_session
        
        with pytest.raises(QubeSyncError, match="Unexpected response: 400"):
            QubeSync.get("test/endpoint")
    
    @patch.object(QubeSync, 'conn')
    def test_post_success(self, mock_connection):
        """Test POST request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": "created"}
        mock_session.post.return_value = mock_response
        mock_connection.return_value = mock_session
        
        body = {"key": "value"}
        result = QubeSync.post("test/endpoint", body)
        
        mock_session.post.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers(),
            json=body
        )
        assert result == {"data": "created"}
    
    @patch.object(QubeSync, 'conn')
    def test_delete_success(self, mock_connection):
        """Test DELETE request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_session.delete.return_value = mock_response
        mock_connection.return_value = mock_session
        
        result = QubeSync.delete("test/endpoint")
        
        mock_session.delete.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers()
        )
        assert result is True
    
    @patch.object(QubeSync, 'post')
    def test_create_connection_success(self, mock_post):
        """Test create_connection success"""
        mock_post.return_value = {"data": {"id": "conn_123", "name": "test_conn"}}
        
        options = {"name": "test_connection"}
        result = QubeSync.create_connection(options)
        
        mock_post.assert_called_once_with("connections", body=options)
        assert result == {"id": "conn_123", "name": "test_conn"}
    
    @patch.object(QubeSync, 'post')
    def test_create_connection_no_id(self, mock_post):
        """Test create_connection error when no ID returned"""
        mock_post.return_value = {"data": {}}
        
        with pytest.raises(QubeSyncError, match="Could not create connection"):
            QubeSync.create_connection({})
    
    @patch.object(QubeSync, 'delete')
    def test_delete_connection(self, mock_delete):
        """Test delete_connection"""
        mock_delete.return_value = True
        
        result = QubeSync.delete_connection("conn_123")
        
        mock_delete.assert_called_once_with("connections/conn_123")
        assert result is True
    
    @patch.object(QubeSync, 'get')
    def test_get_connection(self, mock_get):
        """Test get_connection"""
        mock_get.return_value = {"data": {"id": "conn_123", "name": "test"}}
        
        result = QubeSync.get_connection("conn_123")
        
        mock_get.assert_called_once_with("connections/conn_123")
        assert result == {"id": "conn_123", "name": "test"}
    
    @patch.object(QubeSync, 'post')
    def test_queue_request_with_json(self, mock_post):
        """Test queue_request with request_json"""
        mock_post.return_value = {"data": {"id": "req_123"}}
        
        request = {
            "request_json": {"version": "16.0", "request": {"key": "value"}},
            "webhook_url": "https://example.com/webhook"
        }
        
        result = QubeSync.queue_request("conn_123", request)
        
        mock_post.assert_called_once_with(
            "connections/conn_123/queued_requests",
            {"queued_request": request}
        )
        assert result == {"id": "req_123"}
    
    @patch.object(QubeSync, 'post')
    def test_queue_request_with_xml(self, mock_post):
        """Test queue_request with request_xml"""
        mock_post.return_value = {"data": {"id": "req_123"}}
        
        request = {
            "request_xml": "<xml>test</xml>",
            "webhook_url": "https://example.com/webhook"
        }
        
        result = QubeSync.queue_request("conn_123", request)
        
        mock_post.assert_called_once_with(
            "connections/conn_123/queued_requests",
            {"queued_request": request}
        )
        assert result == {"id": "req_123"}
    
    def test_queue_request_missing_request_data(self):
        """Test queue_request raises error when neither json nor xml provided"""
        request = {"webhook_url": "https://example.com/webhook"}
        
        with pytest.raises(ValueError, match="must have either request_xml or request_json"):
            QubeSync.queue_request("conn_123", request)
    
    @patch.object(QubeSync, 'get')
    def test_get_request(self, mock_get):
        """Test get_request"""
        mock_get.return_value = {"data": {"id": "req_123", "status": "pending"}}
        
        result = QubeSync.get_request("req_123")
        
        mock_get.assert_called_once_with("queued_requests/req_123")
        assert result == {"id": "req_123", "status": "pending"}
    
    @patch.object(QubeSync, 'get')
    def test_get_requests(self, mock_get):
        """Test get_requests"""
        mock_get.return_value = {"data": [{"id": "req_123"}, {"id": "req_456"}]}
        
        result = QubeSync.get_requests("conn_123")
        
        mock_get.assert_called_once_with("connections/conn_123/queued_requests")
        assert result == [{"id": "req_123"}, {"id": "req_456"}]
    
    @patch.object(QubeSync, 'delete')
    def test_delete_request(self, mock_delete):
        """Test delete_request"""
        mock_delete.return_value = True
        
        result = QubeSync.delete_request("req_123")
        
        mock_delete.assert_called_once_with("queued_requests/req_123")
        assert result is True
    
    @patch.object(QubeSync, 'post')
    def test_get_qwc(self, mock_post):
        """Test get_qwc"""
        mock_post.return_value = {"qwc": "qwc_content_here"}
        
        result = QubeSync.get_qwc("conn_123")
        
        mock_post.assert_called_once_with("connections/conn_123/qwc")
        assert result == "qwc_content_here"
    
    @patch.object(QubeSync, 'post')
    def test_generate_password_success(self, mock_post):
        """Test generate_password success"""
        mock_post.return_value = {"data": {"password": "generated_password"}}
        
        result = QubeSync.generate_password("conn_123")
        
        mock_post.assert_called_once_with("connections/conn_123/password")
        assert result == "generated_password"
    
    @patch.object(QubeSync, 'post')
    def test_generate_password_no_password(self, mock_post):
        """Test generate_password error when no password returned"""
        mock_post.return_value = {"data": {}}
        
        with pytest.raises(QubeSyncError, match="Password not found"):
            QubeSync.generate_password("conn_123")
    
    def test_extract_signature_meta_valid(self):
        """Test extract_signature_meta with valid header"""
        header = "t=1234567890,v1=signature1,v1=signature2"
        
        timestamp, signatures = QubeSync.extract_signature_meta(header)
        
        assert timestamp == 1234567890
        assert signatures == ["signature1", "signature2"]
    
    def test_extract_signature_meta_missing_timestamp(self):
        """Test extract_signature_meta with missing timestamp"""
        header = "v1=signature1"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Invalid signature header format"):
            QubeSync.extract_signature_meta(header)
    
    def test_extract_signature_meta_missing_signature(self):
        """Test extract_signature_meta with missing signature"""
        header = "t=1234567890"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Invalid signature header format"):
            QubeSync.extract_signature_meta(header)
    
    def test_extract_signature_meta_with_equals_in_signature(self):
        """Test extract_signature_meta handles equals signs in signature"""
        header = "t=1234567890,v1=sig==with==equals"
        
        timestamp, signatures = QubeSync.extract_signature_meta(header)
        
        assert timestamp == 1234567890
        assert signatures == ["sig==with==equals"]
    
    def test_sign_payload(self):
        """Test sign_payload generates correct signature"""
        payload = "test_payload"
        expected = hmac.new(
            "supersecret".encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        result = QubeSync.sign_payload(payload)
        
        assert result == expected
    
    def test_verify_and_build_webhook_success(self):
        """Test verify_and_build_webhook with valid signature"""
        payload = '{"key": "value"}'
        timestamp = int(time.time())
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        result = QubeSync.verify_and_build_webhook(payload, header)
        
        assert result == {"key": "value"}
    
    def test_verify_and_build_webhook_stale(self):
        """Test verify_and_build_webhook with stale timestamp"""
        payload = '{"key": "value"}'
        timestamp = int(time.time()) - 600  # 10 minutes ago
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        with pytest.raises(StaleWebhookError, match="Timestamp more than 500 seconds old"):
            QubeSync.verify_and_build_webhook(payload, header)
    
    def test_verify_and_build_webhook_invalid_signature(self):
        """Test verify_and_build_webhook with invalid signature"""
        payload = '{"key": "value"}'
        timestamp = int(time.time())
        header = f"t={timestamp},v1=invalid_signature"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Webhook signature mismatch"):
            QubeSync.verify_and_build_webhook(payload, header)
    
    def test_verify_and_build_webhook_custom_max_age(self):
        """Test verify_and_build_webhook with custom max_age"""
        payload = '{"key": "value"}'
        timestamp = int(time.time()) - 100  # 100 seconds ago
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        # Should pass with max_age=200
        result = QubeSync.verify_and_build_webhook(payload, header, max_age=200)
        assert result == {"key": "value"}
        
        # Should fail with max_age=50
        with pytest.raises(StaleWebhookError):
            QubeSync.verify_and_build_webhook(payload, header, max_age=50)

    @patch.object(QubeSync, 'get')
    def test_prebuilt_query_basic(self, mock_get):
        """Test prebuilt_query with basic parameters"""
        mock_get.return_value = {
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "state": "waiting",
                "webhook_state": "not_applicable",
                "connection_id": "conn123"
            }
        }
        
        result = QubeSync.prebuilt_query("conn123", "customers", max_returned=10, active="InactiveOnly")
        
        mock_get.assert_called_once_with("connections/conn123/customers?max_returned=10&active=InactiveOnly")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["state"] == "waiting"

    @patch.object(QubeSync, 'get')
    def test_prebuilt_query_with_iterate(self, mock_get):
        """Test prebuilt_query with iterate=True"""
        mock_get.return_value = {
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "state": "waiting",
                "webhook_state": "not_applicable",
                "connection_id": "conn123"
            }
        }
        
        result = QubeSync.prebuilt_query("conn123", "invoices", iterate=True, max_returned=50)
        
        mock_get.assert_called_once_with("connections/conn123/invoices?max_returned=50&iterate=true")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440001"

    @patch.object(QubeSync, 'get')
    def test_prebuilt_query_no_params(self, mock_get):
        """Test prebuilt_query with no additional parameters"""
        mock_get.return_value = {
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "state": "waiting",
                "webhook_state": "not_applicable",
                "connection_id": "conn123"
            }
        }
        
        result = QubeSync.prebuilt_query("conn123", "vendors")
        
        mock_get.assert_called_once_with("connections/conn123/vendors?")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440002"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_customer_query(self, mock_prebuilt_query):
        """Test customer_query method returns queued request object"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "request_json": {
                "version": "16.0",
                "request": {
                    "name": "CustomerQueryRq",
                    "attributes": {"requestID": "customer_query"}
                }
            },
            "connection_id": "conn123"
        }
        
        result = QubeSync.customer_query("conn123", max_returned=10, active="InactiveOnly")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "customers", max_returned=10, active="InactiveOnly")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440003"
        assert result["state"] == "waiting"
        assert result["request_json"]["request"]["name"] == "CustomerQueryRq"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_customer_query_with_iterate(self, mock_prebuilt_query):
        """Test customer_query with iterate parameter"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440004",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "connection_id": "conn123"
        }
        
        result = QubeSync.customer_query("conn123", iterate=True, max_returned=100)
        
        mock_prebuilt_query.assert_called_once_with("conn123", "customers", iterate=True, max_returned=100)
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440004"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_invoice_query(self, mock_prebuilt_query):
        """Test invoice_query method returns queued request object"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440005",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "request_json": {
                "version": "16.0",
                "request": {
                    "name": "InvoiceQueryRq",
                    "attributes": {"requestID": "invoice_query"}
                }
            },
            "connection_id": "conn123"
        }
        
        result = QubeSync.invoice_query("conn123", max_returned=25, from_modified_date="2024-01-01")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "invoices", max_returned=25, from_modified_date="2024-01-01")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440005"
        assert result["request_json"]["request"]["name"] == "InvoiceQueryRq"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_invoice_query_with_iterate(self, mock_prebuilt_query):
        """Test invoice_query with iterate parameter"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440006",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "connection_id": "conn123"
        }
        
        result = QubeSync.invoice_query("conn123", iterate=True, to_date="2024-12-31")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "invoices", iterate=True, to_date="2024-12-31")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440006"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_vendor_query(self, mock_prebuilt_query):
        """Test vendor_query method returns queued request object"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440007",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "request_json": {
                "version": "16.0",
                "request": {
                    "name": "VendorQueryRq",
                    "attributes": {"requestID": "vendor_query"}
                }
            },
            "connection_id": "conn123"
        }
        
        result = QubeSync.vendor_query("conn123", max_returned=50, active_status="All")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "vendors", max_returned=50, active_status="All")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440007"
        assert result["request_json"]["request"]["name"] == "VendorQueryRq"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_vendor_query_with_iterate(self, mock_prebuilt_query):
        """Test vendor_query with iterate parameter"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440008",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "connection_id": "conn123"
        }
        
        result = QubeSync.vendor_query("conn123", iterate=True, name="DEF")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "vendors", iterate=True, name="DEF")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440008"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_sales_order_query(self, mock_prebuilt_query):
        """Test sales_order_query method returns queued request object"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440009",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "request_json": {
                "version": "16.0",
                "request": {
                    "name": "SalesOrderQueryRq",
                    "attributes": {"requestID": "sales_order_query"}
                }
            },
            "connection_id": "conn123"
        }
        
        result = QubeSync.sales_order_query("conn123", max_returned=20, status="Open")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "sales_orders", max_returned=20, status="Open")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440009"
        assert result["request_json"]["request"]["name"] == "SalesOrderQueryRq"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_sales_order_query_with_iterate(self, mock_prebuilt_query):
        """Test sales_order_query with iterate parameter"""
        mock_prebuilt_query.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "connection_id": "conn123"
        }
        
        result = QubeSync.sales_order_query("conn123", iterate=True, customer_id="cust123")
        
        mock_prebuilt_query.assert_called_once_with("conn123", "sales_orders", iterate=True, customer_id="cust123")
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440010"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_query_methods_empty_response(self, mock_prebuilt_query):
        """Test all query methods handle empty responses"""
        mock_prebuilt_query.return_value = None
        
        # Test all query methods return None for empty responses
        assert QubeSync.customer_query("conn123") is None
        assert QubeSync.invoice_query("conn123") is None
        assert QubeSync.vendor_query("conn123") is None
        assert QubeSync.sales_order_query("conn123") is None

    @patch.object(QubeSync, 'get')
    def test_prebuilt_query_url_encoding(self, mock_get):
        """Test prebuilt_query properly encodes URL parameters"""
        mock_get.return_value = {
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440011",
                "state": "waiting",
                "connection_id": "conn123"
            }
        }
        
        result = QubeSync.prebuilt_query("conn123", "customers", 
                                       name="John & Jane", 
                                       include=["ListID", "FullName"])

        expected_url = "connections/conn123/customers?name=John & Jane&include[]=ListID&include[]=FullName"
        mock_get.assert_called_once_with(expected_url)
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440011"

    @patch.object(QubeSync, 'prebuilt_query')
    def test_query_methods_return_request_object_structure(self, mock_prebuilt_query):
        """Test that query methods return proper request object structure"""
        mock_request_object = {
            "id": "550e8400-e29b-41d4-a716-446655440012",
            "state": "waiting",
            "webhook_state": "not_applicable",
            "request_xml": "<QBXML><QBXMLMsgsRq onError='stopOnError'><CustomerQueryRq requestID='1'><MaxReturned>100</MaxReturned></CustomerQueryRq></QBXMLMsgsRq></QBXML>",
            "request_json": {
                "version": "16.0",
                "request": {
                    "name": "CustomerQueryRq",
                    "attributes": {"requestID": "1"},
                    "children": [{"name": "MaxReturned", "text": "100"}]
                }
            },
            "response_xml": None,
            "response_json": None,
            "webhook_url": "https://example.com/webhook",
            "webhook_attempts": [],
            "webhook_error": None,
            "error": None,
            "links": {
                "self": "/api/v1/connections/123e4567-e89b-12d3-a456-426614174000/queued_requests/550e8400-e29b-41d4-a716-446655440012",
                "ui": "/app/queued_requests/550e8400-e29b-41d4-a716-446655440012",
                "connection_ui": "/app/connections/123e4567-e89b-12d3-a456-426614174000"
            },
            "inserted_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:00:01Z",
            "connection_id": "conn123"
        }
        
        mock_prebuilt_query.return_value = mock_request_object
        
        result = QubeSync.customer_query("conn123", max_returned=100)
        
        # Verify the structure matches the expected request object format
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440012"
        assert result["state"] == "waiting"
        assert result["webhook_state"] == "not_applicable"
        assert "request_xml" in result
        assert "request_json" in result
        assert "response_xml" in result  # Initially None
        assert "response_json" in result  # Initially None
        assert "webhook_url" in result
        assert "links" in result
        assert result["connection_id"] == "conn123"

if __name__ == "__main__":
    pytest.main([__file__])