import requests

def sync_salesforce(api_key, instance_url, data):
    url = f"{instance_url}/services/data/v52.0/sobjects/Contact/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.json()
