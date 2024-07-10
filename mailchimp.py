import requests

def add_to_mailchimp_list(api_url, api_key, data):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(api_url, headers=headers, json=data)
    return response.json()
