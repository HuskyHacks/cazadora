import time
import requests


def authenticate_to_azure():
    """
    Perform the device code flow to authenticate to Azure and obtain an access token and refresh token.
    """
    device_code_url = "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"
    token_url = "https://login.microsoftonline.com/common/oauth2/token?api-version=1.0"

    payload = {
        # Microsoft Office client, publicly available and sufficient to enumerate OAuth apps
        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "resource": "https://graph.microsoft.com"
    }

    device_code_response = requests.post(device_code_url, data=payload)
    device_code_data = device_code_response.json()

    print(
        f"[*] To authenticate, visit https://microsoft.com/devicelogin and enter the code: {device_code_data['user_code']}")

    token_payload = {
        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "resource": "https://graph.microsoft.com",
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "code": device_code_data["device_code"]
    }

    max_wait_time = 900  # 15 minutes
    wait_time = 0
    interval = 10  # 10 seconds

    while wait_time < max_wait_time:
        print("[*] Waiting for device code authentication...")
        token_response = requests.post(token_url, data=token_payload)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data["access_token"]
            # also returns refresh token but we don't need that for our purpose
            return access_token
        elif token_response.status_code == 400:
            error_data = token_response.json()
            if error_data["error"] == "authorization_pending":
                time.sleep(interval)
                wait_time += interval
            else:
                print(f"Error during token retrieval: {error_data}")
                break
        else:
            print(
                f"Error during token retrieval: {token_response.status_code} - {token_response.text}")
            break

    return None
