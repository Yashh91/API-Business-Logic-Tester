
"""Command-line interface for API Business Logic Tester."""

import argparse
import json
import sys
from pathlib import Path

from adapters.rest import RESTAdapter
from api_tester.api_client import APIClient
from api_tester.auth import build_headers
from api_tester.config_loader import load_config
from api_tester.discovery import discover_endpoints, load_openapi
from api_tester.engine.runner import run_scenarios
from api_tester.reporting.json_report import export_json_report
from api_tester.reporting.markdown_report import export_markdown_report
from api_tester.reporting.models import TestReport


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Configure, inspect, and run authorized API "
            "business-logic security tests."
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
        help="List documented endpoints without sending requests.",
    )
    parser.add_argument(
        "--check-connectivity",
        action="store_true",
        help="Send a GET request to the configured API base URL.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the JSON endpoint inventory.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute configured scenarios against the target API.",
    )
    parser.add_argument(
        "--allow-state-changing",
        action="store_true",
        help=(
            "Explicitly allow configured non-GET requests, "
            "which may change application state."
        ),
    )
    parser.add_argument(
        "--report-json",
        default="reports/report.json",
        help="JSON report output path.",
    )
    parser.add_argument(
        "--report-markdown",
        default="reports/report.md",
        help="Markdown report output path.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = load_config(args.config)
        target = config["target"]
        base_url = target["base_url"]
        settings = config.get("settings", {})

        if not isinstance(settings, dict):
            raise ValueError("'settings' must be a YAML mapping.")

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
                    parents=True,
                    exist_ok=True,
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
                timeout=float(settings.get("timeout_seconds", 10)),
                verify_tls=bool(settings.get("verify_tls", True)),
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

        if args.run:
            scenarios = config.get("scenarios", [])

            if not isinstance(scenarios, list):
                raise ValueError("'scenarios' must be a YAML list.")

            if not scenarios:
                raise ValueError(
                    "No scenarios are configured in this profile."
                )

            # Require explicit approval before sending requests that
            # may create, update, or delete application data.
            state_changing = [
                scenario
                for scenario in scenarios
                if isinstance(scenario, dict)
                and scenario.get("enabled", True)
                and str(
                    scenario.get("request_method", "GET")
                ).upper()
                not in {"GET", "HEAD", "OPTIONS"}
            ]

            if state_changing and not args.allow_state_changing:
                raise ValueError(
                    "This profile contains non-GET requests that may "
                    "change application state. Review the scenarios and "
                    "rerun with --allow-state-changing only when you "
                    "have permission and are using suitable test data."
                )

            headers = build_headers(config.get("auth"))

            with RESTAdapter(
                base_url=base_url,
                headers=headers,
                timeout=float(settings.get("timeout_seconds", 10)),
                verify_tls=bool(settings.get("verify_tls", True)),
            ) as adapter:
                results = run_scenarios(scenarios, adapter)

            report = TestReport(
                target_name=target.get("name", "Unnamed API"),
                base_url=base_url,
                results=results,
                metadata={
                    "profile": args.config,
                    "checks_configured": config.get("checks", []),
                },
            )

            json_path = export_json_report(
                report,
                args.report_json,
            )
            markdown_path = export_markdown_report(
                report,
                args.report_markdown,
            )

            print("\nAssessment summary")
            for status, count in report.summary.items():
                print(f"{status.replace('_', ' ').title()}: {count}")

            print(f"\nJSON report: {json_path}")
            print(f"Markdown report: {markdown_path}")

        if not args.openapi and not args.check_connectivity and not args.run:
            print(
                "\nConfiguration validated. No requests were sent."
            )

        if not args.run:
            print(
                "\nSecurity scenario execution was not requested. "
                "Use --run to execute configured scenarios."
            )

        return 0

    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
