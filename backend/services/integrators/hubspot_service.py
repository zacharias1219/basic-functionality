import requests

def sync_hubspot(api_key, data):
    url = f"https://api.hubapi.com/contacts/v1/contact?hapikey={api_key}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.json()
