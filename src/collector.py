import requests
import time
from datetime import datetime

MAX_RETRIES = 5
INITIAL_BACKOFF = 1  # in seconds


def exponential_backoff(retries, retry_after=None):
    if retry_after:
        backoff = retry_after
    else:
        backoff = INITIAL_BACKOFF * (2 ** retries)
    print(f"[*] Rate limited. Retrying in {backoff} seconds...")
    time.sleep(backoff)


def parse_retry_after(retry_after):
    try:
        return int(retry_after)
    except ValueError:
        retry_date = datetime.strptime(
            retry_after, "%a, %d %b %Y %H:%M:%S GMT")
        return max(0, (retry_date - datetime.utcnow()).total_seconds())


def make_api_request(url, headers):
    retries = 0
    all_results = []

    while url:
        while retries < MAX_RETRIES:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                json_response = response.json()
                all_results.extend(json_response.get("value", []))
                url = json_response.get("@odata.nextLink")  # Handle pagination
                retries = 0  # Reset retries on success
                break
            elif response.status_code == 429:
                retries += 1
                retry_after = response.headers.get("Retry-After")
                exponential_backoff(retries, parse_retry_after(retry_after))
            else:
                print(
                    f"[-] Error collecting data from {url}: {response.status_code} - {response.text}")
                return {"value": []}

        if retries >= MAX_RETRIES:
            print(f"[-] Max retries exceeded for {url}.")
            return {"value": all_results}

    return {"value": all_results}


def collect_azure_data(access_token):
    """
    Enumerates the tenant for the authenticated user.
    """
    print("[*] Collecting Initial Azure Data...")
    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}

    data = {
        "tenant": make_api_request("https://graph.microsoft.com/v1.0/organization?$select=id,displayName", headers),
        "applications": make_api_request("https://graph.microsoft.com/v1.0/applications", headers),
        "service_principals": make_api_request("https://graph.microsoft.com/v1.0/servicePrincipals", headers),
        "users": make_api_request("https://graph.microsoft.com/v1.0/users", headers)
    }

    return data
