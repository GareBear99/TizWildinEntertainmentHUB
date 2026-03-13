#!/usr/bin/env python3
import argparse
import json
import requests


def main():
    parser = argparse.ArgumentParser(description="Execute ARC download plan")
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--account", required=True)
    parser.add_argument("--machine", required=True)
    parser.add_argument("--products", nargs="+", required=True)
    parser.add_argument("--channel", default="stable")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--install-root", default="")
    args = parser.parse_args()

    requests.post(f"{args.base}/releases/stage-local", params={"channel": args.channel}, timeout=30).raise_for_status()
    payload = {
        "accountId": args.account,
        "machineId": args.machine,
        "requestedProducts": args.products,
        "channel": args.channel,
        "dryRun": not args.apply,
    }
    if args.install_root:
        payload["installRoot"] = args.install_root
    response = requests.post(f"{args.base}/execute-downloads", json=payload, timeout=60)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
