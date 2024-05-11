import requests

def check_ip_blacklist(ip_address):
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}"
    headers = {
        "Key": "9d548afb6ed6ae61908166f0c4f8f1fbb6ee5af55cd3d3d31a3066e5d012f19d9f0c81b1a5046112",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['data']['isWhitelisted']:
            return True
        elif data['data']['abuseConfidenceScore'] >= 90:
            return False
        else:
            return True