# Lab 01 — OAuth 2.0 Overview

## RESULTS.md

> **Lab Status:** Not Executed  
> **Related Lecture:** `docs/01-oauth/01-overview.md`  
> **Task:** `TASK.md`

---

## 1. Execution Information

| Field | Value |
|---|---|
| Status | `Not Executed` |
| Started At | `TBD` |
| Completed At | `TBD` |
| Environment | `TBD` |
| Runtime | `TBD` |
| Source Revision | `TBD` |

---

## 2. Implementation Summary

Describe what was actually implemented.

```text
Client Application:
TBD

Resource Server:
TBD

Protected Resource:
TBD

Configuration:
TBD

Tests:
TBD
```

Do not describe planned behavior here. Record only what was actually implemented.

---

## 3. Architecture Observed

Record the actual architecture after implementation.

```text
Resource Owner
      │
      ▼
User Agent
      │
      ▼
Client
      │
      ▼
Resource Server
```

Update this diagram if the actual implementation differs.

Document:

```text
Resource Owner:
TBD

Client:
TBD

Authorization Server:
TBD

Resource Server:
TBD
```

---

## 4. Implemented Components

### Client

```text
Location:
TBD

Responsibilities:
TBD
```

### Resource Server

```text
Location:
TBD

Responsibilities:
TBD
```

### Protected Resource

```text
Endpoint:
TBD

Method:
TBD

Purpose:
TBD
```

---

## 5. Verification Results

Record the result of each relevant verification.

| Verification | Expected | Actual | Result |
|---|---|---|---|
| Client starts | Successful startup | TBD | ☐ |
| Client entry point | Successful response | TBD | ☐ |
| Resource Server starts | Successful startup | TBD | ☐ |
| Protected resource | Successful response | TBD | ☐ |
| Unknown resource | Appropriate 4xx response | TBD | ☐ |
| Resource Server unavailable | Explicit failure handling | TBD | ☐ |
| Tests | All relevant tests pass | TBD | ☐ |

---

## 6. Test Evidence

Record concise evidence for the tests actually executed.

### Client

```text
Command:
TBD

Result:
TBD
```

### Resource Server

```text
Command:
TBD

Result:
TBD
```

### Protected Resource

```http
GET /api/profile
```

```text
HTTP Status:
TBD

Response:
TBD
```

### Failure Case

```text
Scenario:
TBD

Expected:
TBD

Actual:
TBD
```

---

## 7. Architecture Evidence

Record how the implementation demonstrates the OAuth roles.

```text
Resource Owner
    → TBD

Client
    → TBD

Authorization Server
    → TBD

Resource Server
    → TBD
```

The Authorization Server should remain identified as an external participant in this Lab unless the implementation explicitly changes that design.

---

## 8. Security Verification

Record only security properties that were actually verified in this Lab.

```text
[ ] No fake OAuth token validation was introduced.
[ ] No fake authentication mechanism was introduced.
[ ] Future OAuth credentials are not logged.
[ ] Client and Resource Server responsibilities remain separated.
[ ] Provider-specific configuration is not embedded.
```

For each verified item, add evidence or a short explanation.

---

## 9. Problems Encountered

Record implementation problems discovered during execution.

Use this format:

```text
Problem:
TBD

Impact:
TBD

Root Cause:
TBD

Resolution:
TBD
```

Add another entry when necessary.

---

## 10. Implementation Decisions

Record decisions that materially affect the implementation.

```text
Decision:
TBD

Reason:
TBD

Alternative Considered:
TBD
```

Only record decisions actually made during the Lab.

---

## 11. Deviations from TASK.md

Document any deviation from the task specification.

```text
Deviation:
TBD

Reason:
TBD

Impact:
TBD
```

If there were no deviations:

```text
No deviations from TASK.md.
```

---

## 12. Acceptance Criteria

Record the final status of each acceptance criterion.

```text
[ ] Client application runs successfully.
[ ] Resource Server runs successfully.
[ ] Client and Resource Server are separate logical components.
[ ] Protected-resource endpoint exists.
[ ] Client can communicate with Resource Server.
[ ] Unknown resources return appropriate errors.
[ ] OAuth roles are explicitly identified.
[ ] Application boundaries are documented.
[ ] Future OAuth configuration placeholders exist.
[ ] No fake Access Token mechanism exists.
[ ] No fake authentication mechanism exists.
[ ] No provider-specific configuration is embedded.
[ ] Basic failure handling is implemented.
[ ] Tests verify implemented behavior.
[ ] Architecture diagram is present.
[ ] Lab is independently runnable.
```

Change each item after execution to:

```text
[x] Passed
```

or:

```text
[ ] Failed / Not Verified
```

---

## 13. Final Result

### Status

```text
TBD
```

Allowed final statuses:

```text
PASS
PASS WITH NOTES
FAIL
```

### Summary

```text
TBD
```

Describe whether the Lab achieved its learning and implementation objectives.

---

## 14. Learning Outcome

After execution, answer:

### What did the implementation demonstrate?

```text
TBD
```

### What became clearer compared with the theory?

```text
TBD
```

### What was different from the initial mental model?

```text
TBD
```

### What remains to be learned?

```text
TBD
```

---

## 15. Next Step

The next Lab should build on the actual state recorded here.

```text
Lab 01
   ↓
OAuth roles established
   ↓
Client + Resource Server foundation
   ↓
Next:
Authorization Request
```

The next Lab must use this result as evidence of the previous implementation state rather than assuming that the previous Lab was completed successfully.
