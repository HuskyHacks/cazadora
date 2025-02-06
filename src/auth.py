import time
import requests
from colorama import Fore
from azure.identity import InteractiveBrowserCredential

GRAPH_RESOURCE = "https://graph.microsoft.com"
GRAPH_SCOPE = GRAPH_RESOURCE + "/.default"
DEVICE_CODE_URL = "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/token?api-version=1.0"


def authenticate_with_device_code():
    """
    Perform the device code flow to authenticate to Azure and obtain an access token.
    """
    payload = {
        # Microsoft Office client, publicly available and sufficient to enumerate OAuth apps
        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "resource": GRAPH_RESOURCE
    }

    device_code_response = requests.post(DEVICE_CODE_URL, data=payload)
    device_code_data = device_code_response.json()

    print(Fore.YELLOW + "[!] To authenticate, visit " + Fore.CYAN + "https://microsoft.com/devicelogin" +
          Fore.YELLOW + " and enter the code: " + Fore.CYAN + device_code_data['user_code'] + Fore.RESET)

    token_payload = {
        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "resource": GRAPH_RESOURCE,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "code": device_code_data["device_code"]
    }

    max_wait_time = 900  # 15 minutes
    wait_time = 0
    interval = 10  # 10 seconds

    while wait_time < max_wait_time:
        print("[*] Waiting for device code authentication...")
        token_response = requests.post(TOKEN_URL, data=token_payload)
        if token_response.status_code == 200:
            token_data = token_response.json()
            # also returns refresh token but we don't need that for our purpose
            return token_data["access_token"]
        elif token_response.status_code == 400:
            error_data = token_response.json()
            if error_data["error"] == "authorization_pending":
                time.sleep(interval)
                wait_time += interval
            else:
                print(f"[-] Error during token retrieval: {error_data}")
                break
        else:
            print(
                f"[-] Error during token retrieval: {token_response.status_code} - {token_response.text}")
            break

    return None


def authenticate_with_azure_sdk():
    """
    Authenticate using Azure SDK's Interactive Web Login and obtain a token with the correct scope.
    """
    try:
        print("[*] Opening web browser for authentication...")
        credential = InteractiveBrowserCredential()
        token = credential.get_token(GRAPH_SCOPE)
        return token.token
    except Exception as e:
        print(f"[-] Azure SDK Web Login authentication failed: {e}")
        return None


def authenticate_to_azure(auth_mode="device_code"):
    """
    Authenticate to Azure using the selected method.

    :param auth_mode: "device_code" or "azure_sdk"
    :return: Access token or None if authentication fails.
    """
    if auth_mode == "azure_sdk":
        print("[*] Attempting authentication using Azure SDK Web Login...")
        token = authenticate_with_azure_sdk()
        if token:
            return token
        print(
            "[-] Azure SDK authentication failed. Falling back to device code authentication...")

    print("[*] Attempting authentication using device code flow...")
    return authenticate_with_device_code()
