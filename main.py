import argparse
import json
from src.auth import authenticate_to_azure
from src.collector import collect_azure_data
from src.hunt import hunt_suspicious_entries, print_hunt_results
from src.logo import print_logo


def main():
    parser = argparse.ArgumentParser(
        description="Azure AD Service Principal & Application Enumerator")
    parser.add_argument("--output", type=str,
                        help="Output file to save JSON data")
    args = parser.parse_args()

    print_logo()

    access_token = authenticate_to_azure()
    if not access_token:
        print("[-] Failed to authenticate.")
        return

    data = collect_azure_data(access_token)

    print("\n[*] Running Initial Security Hunt...")
    hunt_results = hunt_suspicious_entries(data)

    print_hunt_results(hunt_results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
        print(f"[+] Data successfully saved to {args.output}")


if __name__ == "__main__":
    main()
