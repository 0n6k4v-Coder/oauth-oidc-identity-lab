# Lab 01 — OAuth 2.0 Overview

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Lab Type:** Production-oriented Foundation Lab  
> **Related Lecture:** `docs/01-oauth/01-overview.md`  
> **Prerequisite:** Lecture 01 — OAuth 2.0 Overview

---

## 1. Purpose

This Lab turns the concepts introduced in Lecture 01 into a small, runnable application foundation.

The lecture establishes the conceptual model:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

This Lab makes part of that model observable in software:

```text
Browser / User Agent
        ↓
   React Client
        │
        │ HTTP Request
        ▼
FastAPI Resource Server
        │
        ▼
Protected Resource
```

The Authorization Server remains an external protocol participant. It is intentionally not implemented in this Lab.

The objective is not to demonstrate a fake OAuth flow.

The objective is to create a real Client and Resource Server foundation that later Labs can extend with actual OAuth protocol behavior.

---

## 2. Lecture → Lab Mapping

The implementation should be understood as a direct application of Lecture 01 rather than as an unrelated coding exercise.

| Lecture 01 concept | Lab implementation |
|---|---|
| Resource Owner | The person using the application |
| User Agent | The browser |
| Client | React application |
| Resource Server | FastAPI application |
| Protected Resource | `GET /api/profile` |
| Authorization Server | External participant, not yet integrated |
| OAuth 2.0 as authorization | No fake login or fake token mechanism is introduced |

The Lecture answers:

```text
What are the roles?
Why do the roles exist?
How do the roles relate?
```

The Lab answers:

```text
Where are those roles in an actual application?
Which component is responsible for what?
Can the Client communicate with a Resource Server?
What happens when that dependency fails?
```

---

## 3. Scope

### Included

```text
React Client
FastAPI Resource Server
Protected-resource endpoint
Client → Resource Server HTTP communication
Explicit loading / success / error UI states
Basic error handling
Automated Resource Server tests
CORS configuration for local development
Provider-neutral configuration
Production-oriented project boundaries
```

### Intentionally Deferred

```text
Authorization Request
Authorization Response
Authorization Code
Token Exchange
Access Token Validation
Refresh Token
PKCE
OpenID Connect
Microsoft Entra ID
Provider-specific behavior
```

These are introduced only when their corresponding lectures and Labs require them.

---

## 4. Repository Structure

Each Lab is an isolated, reproducible learning snapshot.

```text
01-overview/
├── README.md
└── src/
    ├── client/
    │   └── React application
    │
    └── resource-server/
        └── FastAPI application
```

This Lab does not depend on a working tree from another Lab.

If a later Lab continues from this one, that Lab will contain its own complete source snapshot plus its additional implementation.

---

# 5. Step-by-Step

## Step 1 — Build the Resource Server

Create the Resource Server under:

```text
src/resource-server/
```

Technology:

```text
FastAPI
```

It must expose:

```http
GET /health
GET /api/profile
```

The profile endpoint represents the protected resource boundary for this Lab.

OAuth Access Token validation is intentionally not implemented yet.

### Expected profile response

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

### Connection to Lecture 01

Lecture 01 defines the Resource Server as the component that hosts protected resources.

This step makes that definition concrete by creating an actual HTTP API that owns the resource boundary.

---

## Step 2 — Add Automated Resource Server Tests

Create tests for the behavior introduced in the Lab.

At minimum, verify:

```text
GET /health
    → 200

GET /api/profile
    → 200 + expected response body

GET /api/does-not-exist
    → 404
```

The purpose is to establish that the Resource Server behavior is reproducible rather than manually verified only through a browser.

### Connection to Lecture 01

Lecture 01 introduces the Resource Server as a distinct protocol role.

Automated tests establish that this role has concrete, observable behavior in the implementation rather than existing only as a diagram.

---

## Step 3 — Build the Client

Create the Client under:

```text
src/client/
```

Technology:

```text
React + Vite
```

The initial UI must clearly identify itself as:

```text
OAuth 2.0 Identity Lab
Role: OAuth Client
```

### Connection to Lecture 01

Lecture 01 defines the Client as the application requesting access to a protected resource.

At this stage the React application is the Client, but OAuth authorization has not yet been added.

This preserves the distinction between:

```text
Client role
```

and:

```text
OAuth authorization protocol
```

---

## Step 4 — Add the Client API Layer

Keep HTTP access outside the main UI component.

The Client uses:

```text
src/api/profile.js
```

to call:

```http
GET /api/profile
```

through the browser Fetch API.

### Connection to Lecture 01

The Lecture describes the Client as the application that requests access to protected resources.

This step creates the actual code path through which that Client communicates with the Resource Server.

---

## Step 5 — Add Client Configuration

Configure the Resource Server base URL through a Vite environment variable:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Commit:

```text
.env.example
```

Do not commit the local `.env`.

Do not store secrets in `VITE_*` variables.

### Connection to Lecture 01

Lecture 01 distinguishes protocol concepts from implementation and deployment configuration.

Keeping the endpoint configurable prevents the Client implementation from being unnecessarily tied to one environment.

---

## Step 6 — Connect React to FastAPI

Run both applications and verify the actual application relationship:

```text
Browser
   ↓
React Client
   ↓ HTTP GET
FastAPI Resource Server
   ↓
/api/profile
   ↓
JSON response
   ↓
React UI
```

The Client must have explicit states:

```text
loading
success
error
```

### Connection to Lecture 01

The Lecture establishes that the Client requests protected resources and that the Resource Server hosts them.

This step makes that relationship observable through real HTTP communication.

No OAuth token is used yet.

---

## Step 7 — Configure Local CORS

During local development:

```text
React
http://localhost:5173

FastAPI
http://127.0.0.1:8000
```

These are different origins.

The Resource Server therefore needs explicit CORS configuration for the React development origin.

Use:

```text
http://localhost:5173
```

Do not use a wildcard unless the architecture explicitly requires it.

### Connection to Lecture 01

CORS is not an OAuth mechanism.

It is a browser security mechanism that must be handled because the Client and Resource Server are running on different origins.

This demonstrates an important distinction:

```text
Browser Security
    ≠
OAuth Security
```

---

## Step 8 — Verify API Documentation

Verify that FastAPI exposes:

```text
/docs
/redoc
/openapi.json
```

The API documentation should describe the current endpoints and response schema.

### Connection to Lecture 01

Lecture 01 introduces OAuth as a protocol implemented by real systems.

Making the API contract observable establishes that the Resource Server is a real service rather than a mock endpoint.

---

## Step 9 — Verify Failure Behavior

Stop the Resource Server while leaving the React Client running.

The Client must transition to:

```text
error
```

rather than displaying fabricated or stale resource data.

Expected behavior:

```text
React Client
    ↓
Resource Server unavailable
    ↓
error state
```

Restart the Resource Server and verify that the Client returns to:

```text
success
```

### Connection to Lecture 01

The Lecture emphasizes that protocol understanding must eventually lead to real system behavior.

Testing failure establishes the habit of validating negative paths, not only the happy path.

---

# 6. Execution Results

> **Status:** Completed

## 6.1 Resource Server

The FastAPI Resource Server was successfully created and executed.

Observed:

```text
Uvicorn startup                 PASS
Application startup             PASS
GET /health                     200 OK
GET /api/profile                200 OK
GET /docs                       200 OK
GET /openapi.json               200 OK
GET /redoc                      200 OK
```

The browser also requested:

```text
GET /favicon.ico
```

and received:

```text
404 Not Found
```

This is not considered a Lab failure because no favicon resource is part of the Lab scope.

---

## 6.2 Automated Tests

The Resource Server tests were executed with:

```bash
python -m pytest -v
```

Result:

```text
3 passed
```

Verified behaviors:

```text
test_health             PASSED
test_profile            PASSED
test_unknown_resource   PASSED
```

The initial `pytest` command produced an import-path error:

```text
ModuleNotFoundError: No module named 'app'
```

The issue was resolved by running the test suite through:

```bash
python -m pytest -v
```

which executed successfully.

A dependency warning related to the `TestClient` / HTTPX stack was also identified during development and treated separately from the functional test result.

---

## 6.3 React Client

The React Client was created using:

```text
React + Vite
```

The application rendered successfully in the browser.

Observed UI:

```text
OAuth 2.0 Identity Lab

Role: OAuth Client

Resource Server Response

ID
demo-user

Display Name
Lab User

Resource
protected
```

---

## 6.4 Environment Configuration

The Client successfully loaded:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

This confirmed that the Vite environment configuration was being read correctly.

Temporary console logging was used during verification and then removed.

---

## 6.5 Integration Result

The completed integration was observed as:

```text
Browser
   ↓
React Client
   ↓
GET /api/profile
   ↓
FastAPI Resource Server
   ↓
HTTP 200
   ↓
JSON Resource
   ↓
React UI
```

The first integration attempt failed at the browser layer because CORS had not yet been configured.

Observed failure:

```text
Access to fetch at
'http://127.0.0.1:8000/api/profile'
from origin
'http://localhost:5173'
has been blocked by CORS policy
```

The issue was resolved by explicitly allowing:

```text
http://localhost:5173
```

in FastAPI `CORSMiddleware`.

After the change, the Client successfully retrieved and displayed the Resource Server response.

---

## 6.6 Failure Handling Result

The React Client implemented explicit states:

```text
loading
success
error
```

The Resource Server failure path was exercised during development.

When the Resource Server was unavailable, the Client entered the error state rather than presenting successful resource data.

After restarting the Resource Server, the Client returned to the successful state.

---

# 7. Final Architecture

The completed Lab establishes:

```text
                     User
                       │
                       ▼
                    Browser
                       │
                       ▼
                ┌─────────────┐
                │ React Client│
                │    Client   │
                └──────┬──────┘
                       │
                       │ HTTP
                       ▼
                ┌─────────────┐
                │   FastAPI   │
                │ Resource    │
                │   Server    │
                └──────┬──────┘
                       │
                       ▼
              Protected Resource
```

The corresponding OAuth role mapping is:

```text
User
    → Resource Owner

Browser
    → User Agent

React application
    → Client

FastAPI application
    → Resource Server

Authorization Server
    → External participant, not yet integrated
```

---

# 8. Acceptance Criteria

```text
[x] React Client exists and renders successfully.
[x] FastAPI Resource Server exists and runs successfully.
[x] GET /health returns 200.
[x] GET /api/profile returns 200.
[x] Unknown resource returns 404.
[x] Automated Resource Server tests pass.
[x] React Client successfully calls the Resource Server.
[x] React displays the Resource Server response.
[x] React has loading, success, and error states.
[x] Local CORS is explicitly configured.
[x] No fake OAuth token validation exists.
[x] No fake authentication mechanism exists.
[x] No provider-specific OAuth implementation is included.
[x] API documentation is available.
[x] Client and Resource Server responsibilities remain separate.
```

The following are intentionally **not** acceptance criteria for Lab 01:

```text
[ ] Authorization Server integration
[ ] Authorization Request
[ ] Authorization Code
[ ] Access Token
[ ] PKCE
[ ] OpenID Connect
```

---

# 9. What This Lab Demonstrated

The abstract roles from Lecture 01 are now represented by actual software components:

```text
Resource Owner
      ↓
User

User Agent
      ↓
Browser

Client
      ↓
React

Resource Server
      ↓
FastAPI

Protected Resource
      ↓
GET /api/profile
```

The main learning transition is:

```text
Lecture
   ↓
Conceptual OAuth Roles
   ↓
Lab
   ↓
Actual Application Components
```

The Client and Resource Server are no longer only theoretical roles; they are now observable components with real communication between them.

---

# 10. What This Lab Did Not Demonstrate

This Lab does not implement OAuth authorization itself.

The following remain intentionally deferred:

```text
Authorization Request
Authorization Response
Authorization Code
Token Endpoint
Access Token
Refresh Token
PKCE
OpenID Connect
Microsoft Entra ID
Provider-specific behavior
```

Therefore:

```text
Working Client → Resource Server
    ≠
Complete OAuth implementation
```

The current result is the application foundation required before adding the authorization protocol.

---

# 11. Key Learning Result

The most important distinction established by this Lab is:

```text
Client Role
    ≠
Authentication

Resource Server
    ≠
Authorization Server

HTTP Communication
    ≠
OAuth Authorization
```

The application currently has:

```text
Browser
   ↓
React Client
   ↓
FastAPI Resource Server
```

The next protocol stage will introduce:

```text
React Client
   ↓
Authorization Request
   ↓
Authorization Server
```

The current implementation will be extended rather than discarded.

---

# 12. Next Lecture / Lab

The next stage is:

```text
Lecture 03
OAuth 2.0 Authorization Request
```

The next Lab will introduce the first real OAuth interaction:

```text
Client
   ↓
Authorization Request
   ↓
Authorization Server
```

The current React application becomes the OAuth Client that creates that request.

The current FastAPI application remains the eventual Resource Server.

The learning progression is therefore:

```text
Lab 01
Application Foundation
        ↓
Lab 02
Roles
        ↓
Lab 03
Authorization Request
        ↓
Lab 04
Authorization Code
        ↓
Lab 05
Token Exchange
        ↓
Lab 06
Access Token
        ↓
Lab 07
Refresh Token
        ↓
Lab 08
PKCE
```

Each Lab remains its own reproducible source snapshot.

---

# 13. References

```text
React Documentation
https://react.dev/

Vite Documentation
https://vite.dev/

FastAPI Documentation
https://fastapi.tiangolo.com/

RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html
```

---

# 14. Lab Completion Status

```text
Lab 01 — OAuth 2.0 Overview

Resource Server
    ✅ Complete

Automated Tests
    ✅ Complete

React Client
    ✅ Complete

Client → Resource Server Integration
    ✅ Complete

Failure Handling
    ✅ Verified

OAuth Authorization
    ⏳ Deferred by design

Provider Integration
    ⏳ Deferred by design
```

**Final Result: PASS**

The Lab successfully established a runnable, provider-neutral OAuth application foundation and demonstrated the Client → Resource Server relationship introduced conceptually in Lecture 01.