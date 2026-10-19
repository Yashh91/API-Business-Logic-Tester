
# Architecture

## Overview

API Business Logic Tester is a Python framework for evaluating API business-logic behavior using configurable scenarios and evidence-based results.

The framework separates configuration, HTTP communication, check evaluation, evidence handling, and report generation.

## Component Flow

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
REST Adapter
    |
    v
API Client
    |
    v
Configured API
    |
    v
Response Evaluation
    |
    v
Evidence Collection
    |
    v
JSON / Markdown Reports
```

## Main Components

### Configuration

`api_tester/config_loader.py` loads YAML profiles.

Profiles describe the target API, authentication settings, request scenarios, and expected response behavior.

### HTTP Communication

`api_tester/api_client.py` sends HTTP requests.

`adapters/rest.py` provides a consistent interface for the runner to communicate with a REST API.

### Endpoint Discovery

`api_tester/discovery.py` reads OpenAPI 3.x and Swagger 2.0 specifications and extracts documented endpoint information.

`adapters/openapi.py` exposes the discovered endpoints and specification metadata.

### Scenario Execution

`api_tester/engine/runner.py` converts configured scenarios into validated objects, executes supported checks, and collects results.

The current runner supports authorization-response and input-validation evaluation. Other check types remain unimplemented in the runner.

### Security Checks

The `api_tester/checks/` package contains evaluators for:

- Authorization responses
- Resource ownership
- Input validation
- Duplicate actions
- Business workflow state transitions

These evaluators use supplied responses and evidence. They do not all perform the required verification independently.

### Evidence and Reporting

`api_tester/engine/evidence.py` provides helpers for sanitizing sensitive data and building structured evidence records.

The reporting package summarizes scenario results and exports JSON and Markdown reports.

### Local Testing Lab

`lab/` contains a Flask application and synthetic in-memory data for controlled testing.

The lab provides secure and intentionally vulnerable behavior modes. It is intended for local practice and must not be exposed publicly.

## Result Statuses

| Status | Meaning |
|---|---|
| `PASS` | The configured check's passing condition was met. |
| `VULNERABLE` | Supplied evidence confirms the configured security failure. |
| `INCONCLUSIVE` | Available evidence is insufficient for a reliable conclusion. |
| `NOT_TESTED` | The scenario was disabled, unresolved, or not supported by the current runner. |

A passing status for an individual check does not prove that an entire API is secure.

## Safety

- Test only systems you own or are explicitly authorized to assess.
- Use synthetic accounts and data in the local lab.
- Review state-changing requests before execution.
- Never commit real credentials or sensitive assessment evidence.
- Validate findings manually before reporting vulnerabilities.

## Current Limitations

The framework is being developed incrementally. The runner currently executes only authorization and input-validation scenarios. Duplicate-action, resource-ownership, and state-transition evaluators require additional integration before they can be run as complete automated checks.

The current tests exercise evaluator functions using synthetic responses; end-to-end lab integration still needs to be added.
