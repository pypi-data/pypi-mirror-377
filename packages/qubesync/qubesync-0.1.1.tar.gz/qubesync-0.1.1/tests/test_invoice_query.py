
import requests

url = "https://qubesync.com/api/v1/connections/e54d0685-b0a6-46d4-841e-eaa29fe416c1/invoices"

querystring = {"include[]":["TxnID", "RefNumber"],"request_id":"3"}

headers = {"Authorization": "Basic c2tfMkFnbENld1NGWXAzczhOa2k1R2FSWDIxcnoyNUtiWTVxb1hIaWp1ZG1vOg=="}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())