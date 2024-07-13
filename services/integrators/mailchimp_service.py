import requests
import json

def sync_mailchimp(api_key, list_id, data):
    url = f"https://<dc>.api.mailchimp.com/3.0/lists/{list_id}/members/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.status_code, response.json()
