
# Sample API Business Logic Assessment Report

> **Demonstration only:** All findings and identifiers below are illustrative. They do not represent a real security assessment.

## Assessment Details

- **Target:** Local Business Logic Testing Lab
- **Base URL:** `http://127.0.0.1:8000`
- **Environment:** Local lab
- **Assessment type:** API business logic testing
- **Evidence:** Synthetic responses and test data

## Summary

| Metric | Count |
|---|---:|
| Total scenarios | 5 |
| Pass | 2 |
| Vulnerable | 1 |
| Inconclusive | 1 |
| Not tested | 1 |

## Scenario Results

### AUTH-001 — Protected resource access

**Status:** PASS

**Observation:** The API returned HTTP 403 for a request that was expected to be denied.

**Evidence:**
- Expected denial status: 401 or 403
- Observed status: 403
- Response: `{"error": "Forbidden"}`

**Interpretation:** The response matched the configured denial expectation. This result alone does not establish that all authorization controls are correct.

### INPUT-001 — Invalid quantity validation

**Status:** VULNERABLE

**Observation:** In this illustrative scenario, independent verification confirmed that the application accepted an invalid negative quantity and created an order.

**Evidence:**
- Test input: `quantity = -1`
- Observed status: 201
- Synthetic resource: `order-test-1`
- State verification: Invalid quantity persisted

**Recommended remediation:** Enforce server-side type, range, and business-rule validation before creating an order.

### DUP-001 — Repeated booking submission

**Status:** INCONCLUSIVE

**Observation:** Two responses were received, but the evidence did not establish whether unintended duplicate bookings were created.

**Recommended next step:** Compare resource identifiers and verify application state in the test environment.

### OWN-001 — Resource ownership

**Status:** PASS

**Observation:** The illustrative test data showed that the returned resource owner matched the expected test user.

**Limitation:** This result applies only to the tested scenario and supplied evidence.

### STATE-001 — Invalid workflow transition

**Status:** NOT_TESTED

**Observation:** The current scenario runner does not yet integrate the state-transition evaluator.

**Recommended next step:** Integrate the evaluator with verified before-and-after state checks.

## Important Limitations

- This report is a static example, not generated output from a live run.
- Counts and findings are illustrative.
- Evaluator tests do not replace end-to-end testing.
- A single passing scenario does not prove an API is secure.
- Confirm findings manually before submitting security reports.
