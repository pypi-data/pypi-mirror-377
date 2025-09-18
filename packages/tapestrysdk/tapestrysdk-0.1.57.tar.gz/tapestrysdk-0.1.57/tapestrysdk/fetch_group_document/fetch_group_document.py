import requests

def fetch_group_document(token, tapestry_id, group_ids):
    url = "https://inthepicture.org/admin/fetch_group_documents"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }
    params = {
        "tapestry_id": tapestry_id,
        "group_id": group_ids  # requests will expand list into multiple ?group_id=1&group_id=2
    }

    response = requests.get(url, params=params, headers=headers)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
