
# API Business Logic Tester

A Python framework for testing API business logic using configurable scenarios, structured evidence, and security assessment reports.

The project focuses on authorization behavior, input validation, resource ownership, duplicate actions, and workflow state transitions. It also includes a local Flask lab with synthetic data for controlled practice.

## Key Features

- YAML-based API testing profiles
- HTTP requests through an HTTPX-based client
- OpenAPI 3.x and Swagger 2.0 endpoint discovery
- Bearer-token and API-key authentication helpers
- Authorization-response evaluation
- Input-validation evaluation
- Evaluators for resource ownership, duplicate actions, and state transitions
- Structured JSON and Markdown reports
- Sensitive-field redaction in JSON report output
- Local secure and intentionally vulnerable testing modes
- Automated unit tests using Python's `unittest` and pytest

## Architecture

```text
YAML Profile
     |
     v
Configuration Loader
     |
     v
Scenario Runner
     |
     v
REST Adapter / HTTP Client
     |
     v
Configured API
     |
     v
Evidence-Based Evaluation
     |
     v
JSON and Markdown Reports
```

See [Architecture Documentation](docs/architecture.md) for more details.

## Project Structure

```text
api-business-logic-tester/
├── api_tester/
│   ├── checks/
│   ├── engine/
│   ├── reporting/
│   ├── api_client.py
│   ├── auth.py
│   ├── cli.py
│   ├── config_loader.py
│   └── discovery.py
├── adapters/
├── profiles/
├── lab/
├── tests/
├── docs/
├── reports/
├── requirements.txt
└── pyproject.toml
```

## Requirements

- Python 3.10 or later
- pip
- Permission to test the target API
- A local or authorized test API for assessment scenarios

## Installation

Clone the repository:

```bash
git clone https://github.com/Yashh91/api-business-logic-tester.git
cd api-business-logic-tester
```

Create and activate a virtual environment.

**Linux / Kali Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

## Validate a Configuration

```bash
python -m api_tester.cli --config profiles/example_api.yaml
```

This validates the profile without sending API requests.

## Discover Documented Endpoints

Place an authorized OpenAPI JSON or YAML specification in a local file, then run:

```bash
python -m api_tester.cli --config profiles/example_api.yaml --openapi openapi.json --list-endpoints
```

To export the endpoint inventory:

```bash
python -m api_tester.cli --config profiles/example_api.yaml --openapi openapi.json --list-endpoints --output reports/endpoints.json
```

## Run Configured Scenarios

Review the profile, target, credentials, and request bodies before executing tests.

```bash
python -m api_tester.cli --config profiles/example_api.yaml --run
```

Profiles containing non-GET requests require explicit acknowledgement:

```bash
python -m api_tester.cli --config profiles/example_api.yaml --run --allow-state-changing
```

Only use the second command against an authorized test environment with appropriate test data. Some scenarios may create or modify application resources.

Reports are written by default to:

- `reports/report.json`
- `reports/report.md`

The current runner executes authorization-response and input-validation scenarios. Other evaluators still need runner integration.

## Local Testing Lab

The repository includes a Flask application intended for local testing.

Install the dependencies, then start the lab in secure mode:

```bash
python -m lab.app
```

The application binds to `127.0.0.1:8000`.

To use the intentionally vulnerable mode in an isolated local environment, stop the application and start it with:

**Linux / Kali Linux:**

```bash
LAB_MODE=vulnerable python -m lab.app
```

**Windows PowerShell:**

```powershell
$env:LAB_MODE = "vulnerable"
python -m lab.app
```

Use synthetic data only. Do not expose vulnerable mode to the internet.

The lab uses a synthetic `X-Lab-User` header to select test identities. This is a lab convenience, not production-grade authentication.

## Run Tests

```bash
python -m pytest
```

The test suite currently focuses on individual evaluator functions and report generation. End-to-end integration between the local lab and the scenario runner still needs to be completed.

## Result Statuses

| Status | Meaning |
|---|---|
| `PASS` | The configured passing condition was met. |
| `VULNERABLE` | Supplied evidence confirms a security or business-rule failure. |
| `INCONCLUSIVE` | Available evidence is insufficient. |
| `NOT_TESTED` | The scenario was skipped or is not supported by the current runner. |

A `PASS` result for one scenario does not prove the entire API is secure.

## Documentation

- [Architecture](docs/architecture.md)
- [Supported Checks](docs/supported_checks.md)
- [Sample Report](docs/sample_report.md)

## Security and Responsible Use

Use this framework only on systems you own or have explicit authorization to test.

- Prefer synthetic data and dedicated test accounts.
- Review state-changing requests before execution.
- Keep API credentials out of source control.
- Review and sanitize assessment evidence.
- Verify potential findings before reporting them.

## Current Development Status

This project is under active development. It provides configuration loading, API communication, endpoint discovery, evaluator functions, report generation, and a local practice API.

The next development priorities are:

1. Integrate all five evaluators into the scenario runner.
2. Add end-to-end tests against the local Flask lab.
3. Improve scenario configuration validation and evidence verification.
4. Add reproducible examples and tested installation instructions.

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
