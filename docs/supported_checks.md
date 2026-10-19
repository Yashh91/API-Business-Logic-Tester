
# Supported Security Checks

## Current Implementation Status

The framework contains five check evaluators. However, the current scenario runner only executes authorization-response and input-validation checks. The other evaluators are not yet integrated into automated scenario execution.

| Check | Evaluator available | Runner integrated |
|---|---|---|
| Authorization | Yes | Yes |
| Input validation | Yes | Yes |
| Duplicate actions | Yes | No |
| Resource ownership | Yes | No |
| State transitions | Yes | No |

## 1. Authorization

**Module:** `api_tester/checks/authorization.py`

Evaluates an API response against expected authorization-denial status codes.

Example:
- Expected denial: HTTP 401 or 403
- Observed denial: HTTP 403
- Evaluator result: `PASS`

A `200 OK` response alone does not establish unauthorized access. Independent evidence must confirm that protected data was exposed to a caller without the required permission before the evaluator reports `VULNERABLE`.

## 2. Input Validation

**Module:** `api_tester/checks/input_validation.py`

Evaluates how the API handles inputs that violate application requirements.

Examples:
- Negative order quantity
- Missing required fields
- Invalid identifiers
- Incorrect data types

A configured rejection status such as HTTP 400 or 422 can indicate expected rejection. However, the application response and relevant state should be reviewed to establish whether the invalid input was actually rejected.

Confirmed acceptance of invalid input that violates business requirements can be reported as `VULNERABLE`.

## 3. Duplicate Actions

**Module:** `api_tester/checks/duplicate_actions.py`

Evaluates evidence from two submissions representing the same logical action.

Potential examples:
- Duplicate booking creation
- Repeated order submission
- Repeated payment-related actions in a controlled test environment

Two successful HTTP responses are not enough to establish a vulnerability. Compare resulting resource IDs and application state.

Use `VULNERABLE` only when unintended duplicate creation is independently confirmed.

## 4. Resource Ownership

**Module:** `api_tester/checks/resource_ownership.py`

Evaluates whether a resource belongs to the expected synthetic test user.

Potential examples:
- Accessing another user's order
- Reading another user's booking
- Retrieving a resource through an unauthorized identifier

A missing owner field is not proof of a vulnerability. Verify the caller's identity, resource owner, response content, and applicable authorization requirements.

## 5. State Transitions

**Module:** `api_tester/checks/state_transitions.py`

Evaluates whether an action is allowed for the current business workflow state.

Potential examples:
- Shipping a cancelled order
- Confirming an already completed booking
- Performing a forbidden action before a required prerequisite

A successful HTTP response alone does not prove that an invalid transition occurred. Confirm the resulting application state.

## Result Interpretation

| Status | Interpretation |
|---|---|
| `PASS` | The configured passing condition was met. |
| `VULNERABLE` | Evidence confirms a violation of the configured security or business rule. |
| `INCONCLUSIVE` | More evidence is required. |
| `NOT_TESTED` | The check was not executed. |

## Evidence Quality

A reliable assessment should record:

- The scenario identifier and purpose
- The request method and relative endpoint
- The observed HTTP status
- Relevant sanitized response evidence
- The expected business rule
- Any independently verified state change
- Recommended remediation

Avoid storing real credentials, session cookies, personal information, or unnecessary response data in reports.

## Authorization and Safety

Use only systems you own or are explicitly authorized to test. Prefer a local test environment with synthetic data, particularly for requests that create, update, or delete resources.
