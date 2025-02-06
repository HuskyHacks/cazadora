import argparse
import json
import sys
from src.auth import authenticate_to_azure
from src.collector import collect_azure_data
from src.hunt import hunt_suspicious_entries, print_hunt_results
from src.logo import print_logo


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Simple hunting script for hunting sussy M365 OAuth Apps.")
        parser.add_argument("--output", type=str,
                            help="Output file to save JSON data. Writes all JSON collected from calling the Graph API for more info.")
        parser.add_argument("--auth-mode", type=str, choices=["device_code", "azure_sdk"], default="device_code",
                            help="Authentication method: 'device_code' (default) or 'azure_sdk'.")
        args = parser.parse_args()

        print_logo()

        print("[*] Authenticating to Azure...")

        access_token = authenticate_to_azure(auth_mode=args.auth_mode)

        if not access_token:
            print(
                "[-] Authentication failed. Please check your credentials and try again.")
            sys.exit(1)

        data, status_code = collect_azure_data(access_token)

        if status_code == 403:
            print("\n[-] ERROR: Unauthorized access (403) - User was not found.")
            print(
                "[-] This usually means your account lacks the necessary permissions.")
            print(
                "[-] Ensure your account has the required API permissions in Entra ID.")
            sys.exit(1)

        if status_code != 200:
            print(
                f"[-] Failed to collect data from Graph API (HTTP {status_code}).")
            print("[-] Please check your authentication and try again.")
            sys.exit(1)

        print("\n[*] Running Security Hunt...")
        hunt_results = hunt_suspicious_entries(data)

        print_hunt_results(hunt_results)

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as outfile:
                    json.dump(data, outfile, indent=4)
                print(f"[+] Data successfully saved to {args.output}")
            except Exception as e:
                print(f"[-] Failed to write output file: {e}")

    except KeyboardInterrupt:
        print("\n[!] Script interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
