import os
import json
import requests
import hmac
import hashlib
import time

class QubeSyncError(Exception): pass
class StaleWebhookError(QubeSyncError): pass
class InvalidWebhookSignatureError(QubeSyncError): pass
class ConfigError(QubeSyncError): pass

class QubeSync:
    EXPECTED_SIGNATURE_SCHEMES = ["v1"]

    def base_url():
        return os.getenv("QUBE_URL", "https://qubesync.com/api/v1")

    def default_headers():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def api_key():
        try:
            return os.environ["QUBE_API_KEY"]
        except KeyError:
            raise ConfigError("QUBE_API_KEY not set in environment.")

    def api_secret():
        try:
            return os.environ["QUBE_WEBHOOK_SECRET"]
        except KeyError:
            raise ConfigError("QUBE_WEBHOOK_SECRET not set in environment.")

    def conn():
        session = requests.Session()
        session.auth = (QubeSync.api_key(), "")
        return session

    def get(url, headers={}):
        resp = QubeSync.conn().get(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers})
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json()
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def post(url, body=None, headers={}):
        resp = QubeSync.conn().post(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers}, json=body)
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json()
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def delete(url, headers={}):
        resp = QubeSync.conn().delete(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers})
        if resp.status_code >= 200 and resp.status_code < 300:
            return True
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def create_connection(options={}):
        resp = QubeSync.post("connections", body=options)
        conn = resp.get("data", {})
        if not conn.get("id"):
            raise QubeSyncError(f"Could not create connection: {resp}")
        return conn

    def delete_connection(id):
        return QubeSync.delete(f"connections/{id}")

    def get_connection(id):
        return QubeSync.get(f"connections/{id}").get("data")

    def queue_request(connection_id, request):
        if not (request.get("request_xml") or request.get("request_json")):
            raise ValueError("must have either request_xml or request_json")
        if not request.get("webhook_url"):
            print("Warning: no webhook_url provided")
        return QubeSync.post(f"connections/{connection_id}/queued_requests", {"queued_request": request}).get("data")

    def get_request(id):
        return QubeSync.get(f"queued_requests/{id}").get("data")

    def get_requests(connection_id):
        return QubeSync.get(f"connections/{connection_id}/queued_requests").get("data")

    def delete_request(id):
        return QubeSync.delete(f"queued_requests/{id}")

    def get_qwc(connection_id):
        return QubeSync.post(f"connections/{connection_id}/qwc").get("qwc")

    def generate_password(connection_id):
        resp = QubeSync.post(f"connections/{connection_id}/password")
        password = resp.get("data", {}).get("password")
        if not password:
            raise QubeSyncError(f"Password not found: {resp}")
        return password

    def extract_signature_meta(header, expected_schemes=["v1"]):
        # Example header: t=timestamp,v1=signature1,v1=signature2
        # note: signatures may include '=' characters
        parts = header.split(',')
        timestamp = None
        signatures = []
        for part in parts:
            k, v = part.split('=', 1)
            if k == 't':
                timestamp = int(v)
            elif k in expected_schemes:
                signatures.append(v)
        if timestamp is None or not signatures:
            raise InvalidWebhookSignatureError("Invalid signature header format.")
        return timestamp, signatures

    def sign_payload(payload):
        return hmac.new(
            QubeSync.api_secret().encode("utf-8"), 
            payload.encode("utf-8"), 
            hashlib.sha256
        ).hexdigest()

    def verify_and_build_webhook(body, signature, max_age=500):
        timestamp, signatures = QubeSync.extract_signature_meta(signature, QubeSync.EXPECTED_SIGNATURE_SCHEMES)

        # print for debugging
        print(f"Timestamp: {timestamp}, Signatures: {signatures}")
        if timestamp < time.time() - max_age:
            raise StaleWebhookError(f"Timestamp more than {max_age} seconds old.")
        
        signed_payload = QubeSync.sign_payload(str(timestamp) + '.' + body)
        if any(hmac.compare_digest(signed_payload, sig) for sig in signatures):
            return json.loads(body)
        
        raise InvalidWebhookSignatureError("Webhook signature mismatch")

    def prebuilt_query(connection_id, query_type, iterate=False, **params):
        if iterate:
            params["iterate"] = "true"

        # Handle array parameters - transform lists to multiple params with [] notation
        query_parts = []
        for k, v in params.items():
            if isinstance(v, list):
                # For arrays, add each item with []= notation
                for item in v:
                    query_parts.append(f"{k}[]={item}")
            else:
                query_parts.append(f"{k}={v}")
        
        path = f"connections/{connection_id}/{query_type}?" + "&".join(query_parts)
        return QubeSync.get(path).get("data")

    def customer_query(connection_id, **params):
        return QubeSync.prebuilt_query(connection_id, "customers", **params)

    def invoice_query(connection_id, **params):
        return QubeSync.prebuilt_query(connection_id, "invoices", **params)

    def vendor_query(connection_id, **params):
        return QubeSync.prebuilt_query(connection_id, "vendors", **params)

    def sales_order_query(connection_id, **params):
        return QubeSync.prebuilt_query(connection_id, "sales_orders", **params)
    