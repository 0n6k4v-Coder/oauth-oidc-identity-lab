# Lab 01 — OAuth 2.0 Overview

## TASK.md

> **Lab Type:** Production-oriented Foundation Lab  
> **Related Lecture:** `docs/01-oauth/01-overview.md`  
> **Prerequisite:** Lecture 01 — OAuth 2.0 Overview

---

## 1. Objective

Establish the first runnable application boundary for the OAuth 2.0 learning track and identify the four OAuth 2.0 roles in a real application architecture.

The lab does not implement the complete OAuth authorization flow yet. It establishes a real foundation that later labs can extend without rebuilding the application.

---

## 2. Scope

This lab covers:

```text
Client application
Resource Server
Protected resource boundary
Basic Client → Resource Server communication
OAuth role identification
Application boundary documentation
Basic production-oriented error handling
```

This lab does not cover:

```text
Authorization Request
Authorization Code
Token Exchange
Access Token Validation
Refresh Token
PKCE
OpenID Connect
Microsoft Entra ID
```

---

## 3. Required Architecture

Implement two runnable application components:

```text
Browser / User Agent
        ↓
Client Application
        │
        │ HTTP request
        ▼
Resource Server
        │
        ▼
Protected Resource
```

The Authorization Server remains an external protocol participant and will be introduced in later labs.

---

## 4. Client Requirements

Create the Client application under:

```text
src/client/
```

The Client must:

1. Start successfully in a local development environment.
2. Expose a basic application entry point.
3. Clearly identify itself as an OAuth Client.
4. Be structured so OAuth authorization can be added in later labs.
5. Avoid implementing fake authentication or fake OAuth tokens.

The Client does not need to authenticate the user in this lab.

---

## 5. Resource Server Requirements

Create the Resource Server under:

```text
src/resource-server/
```

The Resource Server must:

1. Start successfully.
2. Expose at least one protected-resource endpoint.
3. Return structured data from the endpoint.
4. Return an appropriate error response for an unknown resource.
5. Be implemented as an independent application boundary.

Example resource endpoint:

```http
GET /api/profile
```

The endpoint is conceptually a protected resource, but actual OAuth Access Token enforcement is intentionally deferred to a later lab.

---

## 6. Role Identification

Document the role mapping used by this implementation.

```text
User
    → Resource Owner

Client Application
    → Client

Future external authorization service
    → Authorization Server

API application
    → Resource Server
```

Do not automatically treat the Browser as the OAuth Client. Identify the actual application performing the Client role.

---

## 7. Application Boundary

Document the responsibility of each application component.

At minimum, answer:

```text
What does the Client do?

What does the Resource Server do?

What is outside the current application?

Where will the Authorization Server participate later?

Where does the protected-resource boundary begin?
```

The documentation must distinguish protocol responsibilities from physical deployment.

---

## 8. Configuration

Create configuration placeholders for future OAuth integration, for example:

```text
AUTHORIZATION_SERVER_ISSUER=
CLIENT_ID=
REDIRECT_URI=
```

These values may remain empty in this lab.

Do not add provider-specific values.
Do not hard-code Microsoft Entra ID settings.

---

## 9. Error Handling

Implement explicit handling for at least:

```text
Unknown resource
Resource Server unavailable
Invalid request to the application
Unexpected server error
```

Use appropriate HTTP status codes and ensure failures are not silently converted into successful responses.

---

## 10. Security Requirements

### Do Not Fake OAuth

Do not implement logic such as:

```text
if token == "fake-token":
    allow
```

### Do Not Fake Authentication

Do not create a fake login flow and present it as OAuth or OIDC authentication.

### Do Not Log Credentials

Do not log or persist:

```text
Passwords
Client Secrets
Authorization Codes
Access Tokens
Refresh Tokens
```

### Keep the Lab Provider-Neutral

No Microsoft Entra ID, Google, Keycloak, Auth0, or other provider-specific settings should be embedded in this lab.

---

## 11. Testing Requirements

Add tests for the behavior introduced by this lab.

### Client

Verify:

```text
Client starts successfully
Client entry point responds successfully
```

### Resource Server

Verify:

```text
GET /api/profile
    → successful response

Unknown endpoint
    → appropriate 4xx response
```

### Failure Behavior

Verify:

```text
Resource Server unavailable
    → Client handles the failure explicitly
```

Tests must verify actual behavior rather than checking only that the processes start.

---

## 12. Architecture Evidence

Create or update:

```text
diagrams/oauth-foundation.md
```

The diagram must show:

```text
Resource Owner
      │
      │ authorization
      ▼
Client
      │
      │ protected resource request
      ▼
Resource Server
```

Also indicate that the Authorization Server is not yet integrated.

Distinguish:

```text
Protocol Role
```

from:

```text
Physical Application / Process
```

---

## 13. Implementation Constraints

Keep the implementation small, but do not use toy shortcuts.

The solution should be:

```text
Runnable
Testable
Explicitly configured
Explicitly error-handled
Responsibility-separated
Extensible by later labs
```

Do not introduce OAuth framework abstractions, provider abstraction layers, microservices, complex infrastructure, or unnecessary database design unless the selected implementation stack genuinely requires them.

---

## 14. Deliverables

The completed lab must contain:

```text
01-overview/
├── README.md
├── TASK.md
├── RESULTS.md
├── src/
│   ├── client/
│   └── resource-server/
└── diagrams/
    └── oauth-foundation.md
```

The exact source layout inside `src/` may follow the selected application stack.

---

## 15. Acceptance Criteria

The lab is accepted only when all of the following are true:

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

---

## 16. Evidence to Record

During execution, record enough evidence to demonstrate that the requirements were actually implemented.

Examples:

```text
Application startup output
HTTP request / response examples
Test results
Error responses
Architecture observations
Relevant implementation decisions
```

Do not copy the entire terminal history into `RESULTS.md`. Record only evidence relevant to the acceptance criteria and learning objectives.

---

## 17. Completion Definition

This lab is complete when the repository contains a working foundation in which:

```text
User
  ↓
Client
  ↓
Resource Server
```

is a real, runnable application relationship, while:

```text
Authorization Server
```

remains an intentionally external dependency for the next stage of the learning path.

The implementation must be ready for later labs to introduce real OAuth authorization without requiring the foundation to be discarded and rebuilt.
