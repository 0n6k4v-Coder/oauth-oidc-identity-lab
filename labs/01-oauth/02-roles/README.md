# Lab 02 — OAuth 2.0 Roles

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Unit:** 01 — OAuth 2.0  
> **Related Lecture:** `docs/01-oauth/02-roles.md`  
> **Lab Type:** Architecture and Role-Mapping Lab  
> **Status:** Completed

---

## 1. Purpose

This Lab turns the OAuth 2.0 role model from Lecture 02 into concrete, independently runnable application components.

The Lab contains three software components:

```text
Client
    → React

Authorization Server
    → FastAPI :9000

Resource Server
    → FastAPI :8000
```

The Resource Owner and User Agent are represented by the human user and browser:

```text
Resource Owner
    → User

User Agent
    → Browser
```

### Critical Scope Boundary

The Authorization Server is **present only as an independent, runnable role component in this Lab**.

It is **not connected to the Client yet**.

The current working application flow is only:

```text
User
  ↓
Browser
  ↓
React Client
  ↓
Resource Server
  ↓
Protected Resource
```

The OAuth authorization interaction begins in Lab 03.

---

# 2. Learning Objectives

By completing this Lab, the learner should be able to:

* Identify the four primary OAuth 2.0 roles.
* Identify the User Agent without confusing it with an OAuth role.
* Map the roles to concrete software components.
* Distinguish the Authorization Server from the Resource Server.
* Explain that the Authorization Server can exist before the OAuth protocol flow is implemented.
* Explain that the current Client → Resource Server request is not an OAuth authorization flow.
* Understand that OAuth roles describe responsibilities rather than mandatory physical deployment boundaries.
* Understand that Authorization Server and Resource Server responsibilities may be deployed separately or together.
* Distinguish OAuth roles from frameworks, processes, physical servers, repositories, and databases.

---

# 3. Role Mapping

```text
Resource Owner
    → User

User Agent
    → Browser

Client
    → React

Authorization Server
    → FastAPI :9000

Resource Server
    → FastAPI :8000
```

The Client is treated as a browser-based public Client for security reasoning. The behavioral consequences of that classification are intentionally deferred to later Labs, especially PKCE.

---

# 4. Repository Structure

```text
02-roles/
├── README.md
└── src/
    ├── authorization-server/
    │   ├── app/
    │   │   └── main.py
    │   ├── tests/
    │   │   └── test_health.py
    │   └── requirements.txt
    │
    ├── client/
    │   └── React + Vite application
    │
    └── resource-server/
        ├── app/
        │   └── main.py
        ├── tests/
        │   └── test_profile.py
        └── requirements.txt
```

The components are kept in separate source trees so their OAuth responsibilities are visible to the learner.

This separation is a **Lab architecture choice**, not an OAuth deployment requirement.

---

# 5. Step-by-Step

## Step 1 — Preserve the Lab 01 Foundation

Lab 02 starts from the working Client and Resource Server state established in Lab 01.

```text
Lab 01
Client + Resource Server
        ↓
Lab 02
Client + Resource Server
        +
Authorization Server component
```

### Learning Result

Each Lab remains a reproducible source snapshot instead of silently modifying the previous Lab.

---

## Step 2 — Identify the Resource Owner

In this user-delegated scenario:

```text
Resource Owner
    → User
```

There is no `resource-owner/` service because the Resource Owner is an OAuth role representing the entity capable of granting access to the protected resource.

### Learning Result

An OAuth role does not imply a dedicated application or server.

---

## Step 3 — Identify the User Agent

The browser is the User Agent:

```text
User
  ↓
Browser
```

The browser provides the interaction environment through which the user operates the Client.

### Learning Result

```text
User Agent
    ≠
OAuth Client
```

The browser is not counted as one of the four primary OAuth roles defined by RFC 6749.

---

## Step 4 — Identify the Client

The React application performs the Client role:

```text
React
  ↓
Client
```

The Client currently requests the profile resource directly from the Resource Server.

### Learning Result

The Client is the application requesting access; it is not the Resource Owner merely because it acts on the user's behalf.

---

## Step 5 — Identify the Resource Server

The FastAPI application on port `8000` performs the Resource Server role:

```text
FastAPI :8000
    ↓
Resource Server
```

It exposes:

```http
GET /health
GET /api/profile
```

The `/api/profile` endpoint represents the protected resource used by the Client in this Lab.

### Learning Result

The Resource Server is the component responsible for serving and protecting resources.

---

## Step 6 — Add the Authorization Server Component

The FastAPI application on port `9000` represents the Authorization Server role:

```text
FastAPI :9000
    ↓
Authorization Server
```

Its current implementation exposes only:

```http
GET /health
```

It does not yet expose:

```text
/authorize
/token
```

### Learning Result

The Authorization Server role can exist as an independently runnable component before actual OAuth authorization behavior is implemented.

---

## Step 7 — Test the Authorization Server Independently

The Authorization Server test suite verifies:

```text
GET /health → 200
Unknown route → 404
```

Observed execution:

```text
2 passed
```

### Learning Result

The Authorization Server is independently testable even though it is not yet part of the Client's request flow.

---

## Step 8 — Verify the Resource Server

Verify:

```text
GET http://127.0.0.1:8000/health
```

and:

```text
GET http://127.0.0.1:8000/api/profile
```

Observed profile:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

### Learning Result

The Resource Server is independently reachable and serves the resource consumed by the Client.

---

## Step 9 — Verify the Client → Resource Server Flow

Start the React application and open:

```text
http://localhost:5173
```

The Client calls:

```text
GET http://127.0.0.1:8000/api/profile
```

The observed UI is:

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

### Learning Result

The actual working application path is:

```text
User
  ↓
Browser
  ↓
React Client
  ↓
Resource Server
  ↓
Protected Resource
```

This is **not yet an OAuth authorization flow** because no authorization request, authorization code, Access Token, or Token Endpoint interaction exists.

---

## Step 10 — Verify That the Authorization Server Is Not in the Current Flow

The Client's API implementation currently calls the configured Resource Server URL for `/api/profile`.

Therefore:

```text
React Client
     │
     │ GET /api/profile
     ▼
Resource Server :8000
```

There is currently no:

```text
React Client
     │
     │ Authorization Request
     ▼
Authorization Server :9000
```

### Learning Result

This distinction is essential:

```text
Authorization Server exists
    ≠
Authorization Server is currently being used by the Client
```

---

## Step 11 — Same Framework Experiment

Both backend components use FastAPI:

```text
FastAPI :9000
    → Authorization Server

FastAPI :8000
    → Resource Server
```

They remain different OAuth roles.

### Learning Result

```text
Framework
    ≠
OAuth Role
```

---

## Step 12 — Same Server Experiment

OAuth does not require the Authorization Server and Resource Server to run on different physical servers.

Conceptually:

```text
Single Server
    ├── Authorization Server responsibility
    └── Resource Server responsibility
```

RFC 6749 explicitly permits the Authorization Server and Resource Server to be the same server or separate entities.

### Learning Result

```text
Physical Server
    ≠
OAuth Role
```

---

## Step 13 — Same Process Experiment

The two responsibilities may also be implemented within one application process:

```text
Single Application
    ├── Authorization Server responsibility
    └── Resource Server responsibility
```

The protocol responsibilities remain distinct.

### Learning Result

```text
Process Boundary
    ≠
OAuth Role Boundary
```

---

## Step 14 — Same Database Experiment

OAuth does not require a separate database for each role.

Conceptually:

```text
Authorization Server ─┐
                      ├── Database
Resource Server ──────┘
```

The persistence topology is an application architecture decision.

### Learning Result

```text
Database Boundary
    ≠
OAuth Role Boundary
```

---

# 6. Final Architecture

The **actual Lab 02 state** is:

```text
                    Resource Owner
                          │
                          ▼
                       Browser
                    (User Agent)
                          │
                          ▼
                    React Client
                          │
                          │ GET /api/profile
                          ▼
                 Resource Server :8000
                          │
                          ▼
                   Protected Resource


             Authorization Server :9000
             ───────────────────────
             Independent component
             /health only
             Not connected to Client yet
```

The architecture therefore has three software components, but only one application request flow has been implemented:

```text
Client → Resource Server
```

The Authorization Server is currently independent.

---

# 7. Execution Results

## Authorization Server

```text
GET /health        → 200 OK
GET /docs          → 200 OK
GET /openapi.json  → 200 OK
```

Automated tests:

```text
2 passed
```

These results establish that the Authorization Server component runs independently.

They do **not** establish an OAuth authorization flow.

---

## Resource Server

Observed:

```text
GET /health
    → 200 OK

GET /api/profile
    → 200 OK
```

The profile response was successfully returned to the Client.

---

## Client

The React Client rendered successfully and displayed the Resource Server response:

```text
ID: demo-user
Display Name: Lab User
Resource: protected
```

---

## Client → Resource Server

The Client successfully requested:

```text
http://127.0.0.1:8000/api/profile
```

The browser integration required local CORS configuration because the development origins differ:

```text
Client
http://localhost:5173

Resource Server
http://127.0.0.1:8000
```

Final integration result:

```text
PASS
```

---

# 8. Acceptance Criteria

```text
[x] Client exists and renders.
[x] Authorization Server exists and runs independently.
[x] Resource Server exists and runs independently.
[x] Authorization Server health endpoint works.
[x] Resource Server health endpoint works.
[x] Resource Server protected-resource endpoint works.
[x] Authorization Server automated tests pass.
[x] Resource Server automated tests remain valid.
[x] React Client communicates with the Resource Server.
[x] Resource Owner is identified.
[x] User Agent is identified.
[x] Client is identified.
[x] Authorization Server is identified.
[x] Resource Server is identified.
[x] Client Type is understood as a classification, not a role.
[x] Same-framework distinction is understood.
[x] Same-server distinction is understood.
[x] Same-process distinction is understood.
[x] Same-database distinction is understood.
[x] Authorization Server is intentionally independent from the current Client flow.
[x] Authorization Request is intentionally deferred.
[x] Authorization Code is intentionally deferred.
[x] Token Exchange is intentionally deferred.
[x] Access Token is intentionally deferred.
[x] Refresh Token is intentionally deferred.
[x] PKCE is intentionally deferred.
```

---

# 9. What We Learned

The four primary OAuth roles are:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The Browser/User Agent participates in the interaction but is not a fifth primary OAuth role.

The Lab now demonstrates these mappings:

```text
User
    → Resource Owner

Browser
    → User Agent

React
    → Client

FastAPI :9000
    → Authorization Server

FastAPI :8000
    → Resource Server
```

The central architectural lesson is:

```text
OAuth Role
    ≠
Framework

OAuth Role
    ≠
Process

OAuth Role
    ≠
Physical Server

OAuth Role
    ≠
Database
```

The central execution lesson is:

```text
Authorization Server
    ✅ Exists
    ✅ Runs
    ✅ Tested
    ❌ Not connected to Client yet

Client
    ✅ Connected to Resource Server
```

---

# 10. What This Lab Did Not Demonstrate

This Lab does not implement the OAuth authorization protocol.

It intentionally does not implement:

```text
Authorization Request
Authorization Endpoint
Resource Owner authentication
Consent
Authorization Code
Token Endpoint
Access Token issuance
Refresh Token
PKCE
OpenID Connect
Provider integration
```

Those features are introduced in later Labs according to the learning sequence.

---

# 11. Relationship to Lab 03

Lab 02 establishes the participants.

Lab 03 introduces the first actual OAuth interaction.

Current state:

```text
React Client
      │
      │ ordinary HTTP request
      ▼
Resource Server
```

Next state:

```text
React Client
      │
      │ Authorization Request
      ▼
Authorization Server
```

This is where the Authorization Server will stop being an independent, unused component and become part of the actual OAuth protocol flow.

---

# 12. Standards Basis

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Relevant to this Lab:
- Resource Owner
- Client
- Authorization Server
- Resource Server
- Authorization Endpoint
- Token Endpoint
- Authorization Code

RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Provides the current security baseline that will be applied
as later Labs implement the actual authorization and token flows.
```

---

# 13. Completion Status

```text
Lab 02 — OAuth 2.0 Roles

Resource Owner
    ✅ Identified

User Agent
    ✅ Identified

Client
    ✅ Implemented

Authorization Server
    ✅ Implemented as an independent component
    ✅ Independently tested
    ⏳ OAuth protocol behavior deferred

Resource Server
    ✅ Implemented
    ✅ Independently verified
    ✅ Client integration working

Actual Client Flow
    ✅ Client → Resource Server

Authorization Server Integration
    ⏳ Deferred to Lab 03
```

**Final Result: PASS**

Lab 02 successfully demonstrates the OAuth 2.0 role model and makes the boundaries between the roles observable without prematurely implementing the OAuth authorization protocol.