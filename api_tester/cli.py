
"""Command-line interface for API Business Logic Tester."""

import argparse
import json
import sys
from pathlib import Path

from api_tester.auth import build_headers
from api_tester.config_loader import load_config
from api_tester.discovery import discover_endpoints, load_openapi
from api_tester.api_client import APIClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Configure and inspect APIs for authorized "
            "business-logic security testing."
        )
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the YAML API profile.",
    )
    parser.add_argument(
        "--openapi",
        help="Optional local OpenAPI JSON/YAML specification.",
    )
    parser.add_argument(
        "--list-endpoints",
        action="store_true",
        help="List documented endpoints without sending API requests.",
    )
    parser.add_argument(
        "--check-connectivity",
        action="store_true",
        help="Send a GET request to the configured base URL.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for a JSON endpoint inventory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = load_config(args.config)
        target = config["target"]
        base_url = target["base_url"]

        print("API Business Logic Tester")
        print(f"Target profile: {target.get('name', 'Unnamed API')}")
        print(f"Base URL: {base_url}")

        if args.openapi:
            spec = load_openapi(args.openapi)
            endpoints = discover_endpoints(spec)

            print(f"\nDocumented endpoints: {len(endpoints)}")

            if args.list_endpoints:
                for endpoint in endpoints:
                    summary = endpoint.get("summary") or ""
                    print(
                        f"{endpoint['method']:7} "
                        f"{endpoint['path']} {summary}"
                    )

            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(
                    parents=True, exist_ok=True
                )
                output_path.write_text(
                    json.dumps(endpoints, indent=2),
                    encoding="utf-8",
                )
                print(f"\nEndpoint inventory saved: {output_path}")

        elif args.list_endpoints:
            print(
                "\nNo OpenAPI specification supplied. "
                "Use --openapi to list documented endpoints."
            )

        if args.check_connectivity:
            headers = build_headers(config.get("auth"))

            with APIClient(
                base_url=base_url,
                headers=headers,
            ) as client:
                result = client.request("GET", "/")

            if not result["ok"]:
                print(
                    f"\nConnectivity check failed: {result['error']}",
                    file=sys.stderr,
                )
                return 1

            print(
                "\nConnectivity request completed. "
                f"HTTP status: {result['status_code']}"
            )

        if not args.openapi and not args.check_connectivity:
            print(
                "\nConfiguration validated. No requests were sent."
            )

        print(
            "\nSecurity checks are not implemented yet; "
            "this command currently validates configuration, "
            "discovers endpoints, and optionally checks connectivity."
        )
        return 0

    except (OSError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
