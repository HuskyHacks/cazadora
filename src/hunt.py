import re
from colorama import Fore, Back, Style
from datetime import datetime

# https://www.proofpoint.com/us/blog/cloud-security/revisiting-mact-malicious-applications-credible-cloud-tenants
SUSPICIOUS_REPLY_URL_PATTERN = re.compile(r"^http://localhost:\d+/access/?$")

# https://huntresslabs.github.io/rogueapps/
TRAITORWARE_APPS = [
    "em client",
    "perfectdata software",
    "newsletter software supermailer",
    "cloudsponge",
    "rclone"
]


def hunt_suspicious_entries(data):
    """
    Hunts for suspicious service principals based on given criteria:
    - Apps named with non-alphanumeric character names.
    - Apps named after users (matching displayName or full UPN).
    - Apps with the suspicious reply URL per Proofpoint's MACT campaign 1445 intel.
    - Apps named "Test" or "Test App" (case-insensitive) or some varient.
    - Apps named in the "traitorware" list (case-insensitive).
    """
    results = {
        "non_alphanumeric_names": [],
        "name_matches_assigned_user": [],
        "suspicious_reply_urls": [],
        "apps_named_test_or_close": [],
        "traitorware_apps": []
    }

    service_principals = data.get("service_principals", {}).get("value", [])
    users_list = data.get("users", {}).get("value", [])

    users = {}
    for user in users_list:
        if isinstance(user, dict):
            user_id = user.get("id", "unknown")
            display_name = user.get("displayName", "").strip().lower()
            user_principal_name = user.get(
                "userPrincipalName", "").strip().lower()

            users[user_id] = [display_name, user_principal_name]

    non_alphanumeric_pattern = re.compile(r"^[^a-zA-Z0-9]+$")
    test_app_pattern = re.compile(
        r"^(test|test app|app test|apptest)$", re.IGNORECASE)

    traitorware_patterns = {name.lower() for name in TRAITORWARE_APPS}

    for sp in service_principals:
        sp_id = sp.get("id", "unknown")
        sp_name = sp.get("displayName", "Unknown").strip().lower()
        reply_urls = sp.get("replyUrls", [])

        # 1. Flag Service Principals with only Non-Alphanumeric Characters in Name
        if non_alphanumeric_pattern.match(sp_name):
            results["non_alphanumeric_names"].append(sp)

        # 2. Flag Service Principals Named After a User (Display Name or Full UPN)
        for user_display_name, user_upn in users.values():
            if sp_name == user_display_name or sp_name == user_upn:
                results["name_matches_assigned_user"].append(sp)
                break

        # 3. Flag Service Principals with Suspicious Reply URL per Proofpoint intel
        if any(SUSPICIOUS_REPLY_URL_PATTERN.match(url) for url in reply_urls):
            results["suspicious_reply_urls"].append(sp)

        # 4. Flag Service Principals Named "Test" or "Test App" or somethign close
        if test_app_pattern.match(sp_name):
            results["apps_named_test_or_close"].append(sp)

        # 5. Flag Service Principals Named in "Traitorware" List
        if sp_name in traitorware_patterns:
            results["traitorware_apps"].append(sp)

    return results


def print_hunt_results(results):
    """
    Prints out the findings in a structured, readable format, highlighting only the app name:
    - Medium Confidence: Yellow Foreground
    - High Confidence: Red Foreground
    - Extremely High Confidence: Red Background, Yellow Foreground
    """
    print("\n=== HUNT RESULTS ===")

    CONFIDENCE_COLORS = {
        "apps_named_test_or_close": Fore.YELLOW,
        "non_alphanumeric_names": Fore.RED,
        "name_matches_assigned_user": Fore.RED,
        "suspicious_reply_urls": Back.RED + Fore.YELLOW,
        "traitorware_apps": Fore.RED
    }

    for category, entries in results.items():
        if entries:
            print(f"\n[!] {category.replace('_', ' ').title()}:")

            for sp in entries:
                sp_id = sp.get("id", "Unknown ID")
                sp_name = sp.get("displayName", "Unknown Name")
                created_date = sp.get("createdDateTime", "Unknown Date")
                reply_urls = sp.get("replyUrls", [])

                name_color = CONFIDENCE_COLORS.get(category, Fore.RESET)

                try:
                    created_date = datetime.strptime(
                        created_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass

                print(f"\n  📌 Service Principal Found")
                print(
                    f"   ├─ 🏷️  Name: {name_color}{sp_name}{Fore.RESET}{Back.RESET}")
                print(f"   ├─ 🆔  ID: {sp_id}")
                print(f"   ├─ 📅  Created: {created_date}")

                if category == "suspicious_reply_urls":
                    print("   ├─ 🔗  Suspicious Reply URL(s):")
                    for url in reply_urls:
                        if SUSPICIOUS_REPLY_URL_PATTERN.match(url):
                            print(f"   │  ├─ {url}")

                print("   └──────────────────────────")

    if not any(results.values()):
        print(
            "\n[+] No suspicious entries found. I'd still recommend that you audit your applications!")
    else:
        print("\n=== LEGEND ===")
        print(Fore.YELLOW + "🟡 Medium Confidence:" +
              Fore.RESET + " Apps that may be test/dev-related. Intel notes that malicious apps can be called 'test' or 'test app' but many legitimate dev-related apps are as well.")
        print(Fore.RED + "🔴 High Confidence:" + Fore.RESET +
              " Apps that are likely indicators of suspicious activity. Prioritize investigation.")
        print(Back.RED + Fore.YELLOW + "🚨 Extremely High Confidence:" +
              Fore.RESET + Back.RESET + " Apps that should be investigated immediately.")
        print(
            "\n[!] Please audit your Enterprise Applications and Application Registrations for the apps identified by this script!")
