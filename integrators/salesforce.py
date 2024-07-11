import requests

def get_salesforce_data(api_url, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(api_url, headers=headers)
    return response.json()
