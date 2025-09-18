import requests
import json

project_id = "hurozo"
user_id = "FKiqfnrG80ZkkzMI0L9AM8ZbMOY2"
api_key = "AIzaSyD2SmbNJTmnzEiYGzujQPbTX1VixZqxqpo"  # from Firebase project settings

# Firestore REST base URL
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:runQuery?key={api_key}"

# ---- Case 1: remote_requests as SUBCOLLECTION under user doc ----
payload_subcollection = {
    "structuredQuery": {
        "from": [{"collectionId": "remote_requests"}],
        "where": {
            "fieldFilter": {
                "field": {"fieldPath": "agent"},
                "op": "EQUAL",
                "value": {"stringValue": "my_remote_agent"}
            }
        },
        "orderBy": [{"field": {"fieldPath": "createdAt"}, "direction": "ASCENDING"}]
    },
    "parent": f"projects/{project_id}/databases/(default)/documents/users/{user_id}"
}

# ---- Case 2: remote_requests as TOP-LEVEL collection ----
payload_top_level = {
    "structuredQuery": {
        "from": [{"collectionId": "remote_requests"}],
        "where": {
            "fieldFilter": {
                "field": {"fieldPath": "agent"},
                "op": "EQUAL",
                "value": {"stringValue": "my_remote_agent"}
            }
        },
        "orderBy": [{"field": {"fieldPath": "createdAt"}, "direction": "ASCENDING"}]
    },
    "parent": f"projects/{project_id}/databases/(default)/documents"
}

# Pick which payload to test first:
payload = payload_subcollection  # or payload_top_level

resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
print("Status:", resp.status_code)
print(resp.text)

