# Lab 02 — OAuth 2.0 Roles

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Unit:** 01 — OAuth 2.0  
> **Related Lecture:** `docs/01-oauth/02-roles.md`  
> **Lab Type:** Architecture and Role-Mapping Lab  
> **Status:** Completed

---

## 1. Purpose

This Lab turns the conceptual OAuth 2.0 role model from Lecture 02 into a small, runnable multi-component system.

Lecture 02 defines the four primary OAuth roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The Lab makes the roles observable through actual applications:

```text
Resource Owner
      ↓
    User
      ↓
  User Agent
   Browser
      ↓
   Client
    React
      │
      ├──────────────► Authorization Server
      │                  FastAPI :9000
      │
      └──────────────► Resource Server
                         FastAPI :8000
```

The Authorization Server is present as a real, independently runnable component, but the OAuth authorization protocol itself is intentionally not implemented in this Lab.

---

# 2. Learning Objectives

By completing this Lab, the learner should be able to:

* Identify the four primary OAuth 2.0 roles in a running system.
* Distinguish the Resource Owner from the Client.
* Distinguish the User Agent from the Client.
* Distinguish the Authorization Server from the Resource Server.
* Map logical OAuth roles to concrete application components.
* Understand that OAuth roles are protocol responsibilities rather than mandatory physical servers.
* Understand that the Authorization Server and Resource Server may be deployed separately or together.
* Understand that framework, process, server, repository, and database boundaries do not define OAuth roles.
* Recognize that the current Client → Resource Server request is not yet an OAuth authorization flow.

---

# 3. Lecture → Lab Mapping

| Lecture 02 concept | Lab implementation |
|---|---|
| Resource Owner | User interacting with the application |
| User Agent | Browser |
| Client | React application |
| Authorization Server | FastAPI application on port `9000` |
| Resource Server | FastAPI application on port `8000` |
| Protected Resource | `GET /api/profile` |
| Client Type | React/browser Client is treated as a public Client conceptually |
| Role separation | Authorization Server and Resource Server are separate Lab components |

The lecture answers:

```text
What are the OAuth roles?
```

The Lab answers:

```text
Where do those roles exist in an actual application?
How can we observe the boundaries between them?
Does a role require a dedicated physical server?
```

---

# 4. Scope

## Included

```text
React OAuth Client
FastAPI Authorization Server component
FastAPI Resource Server component
Independent service startup
Independent service health checks
Resource Server automated tests
Authorization Server automated tests
Client → Resource Server integration
Role identification
Role-separation experiments
```

## Intentionally Deferred

```text
Authorization Request
Authorization Endpoint behavior
Authorization Code issuance
Token Endpoint behavior
Access Token issuance
Refresh Token
PKCE
OpenID Connect
Provider integration
```

Those belong to later Labs.

---

# 5. Repository Structure

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
    │   ├── src/
    │   ├── public/
    │   ├── package.json
    │   ├── package-lock.json
    │   └── ...
    │
    └── resource-server/
        ├── app/
        │   └── main.py
        ├── tests/
        │   └── test_profile.py
        └── requirements.txt
```

Lab 02 keeps the Client, Authorization Server, and Resource Server as separate source trees so the learner can see the role boundaries clearly.

This is a **learning architecture choice**, not a requirement of OAuth itself.

---

# 6. Step-by-Step

## Step 1 — Start From the Lab 01 Foundation

Lab 02 preserves the working Client and Resource Server foundation from Lab 01.

Conceptually:

```text
Lab 01
Client + Resource Server
        ↓
Lab 02
Client + Resource Server
        +
Authorization Server
```

The purpose is to extend the application without rewriting the previous Lab.

### Learning Result

A later Lab should be a reproducible source snapshot rather than an undocumented modification of an earlier Lab.

---

## Step 2 — Identify the Existing Client

The React application is the OAuth Client.

```text
React
  ↓
Client
```

The Client requests access to protected resources but does not become the Resource Owner merely because it acts on the user's behalf.

### Learning Result

```text
Client
    ≠
Resource Owner
```

The roles describe different responsibilities.

---

## Step 3 — Identify the User Agent

The browser is the User Agent.

```text
User
  ↓
Browser
  ↓
React Client
```

The User Agent is part of the interaction environment but is not one of OAuth's four primary roles defined by RFC 6749.

### Learning Result

```text
Browser
    ≠
Client
```

The browser can run the Client while remaining the User Agent through which the Resource Owner interacts.

---

## Step 4 — Add the Authorization Server Component

Create:

```text
src/authorization-server/
```

The component is intentionally minimal for this Lab.

It provides a health endpoint:

```http
GET /health
```

and identifies itself as:

```text
service = authorization-server
role = authorization_server
```

The implementation uses FastAPI and a typed Pydantic response model.

### Learning Result

The Authorization Server role now exists as a real, independently runnable application component.

It is deliberately **not** yet a complete OAuth Authorization Server.

---

## Step 5 — Test the Authorization Server Independently

The Authorization Server has automated tests for:

```text
GET /health → 200
Unknown route → 404
```

The actual executed result was:

```text
2 passed
```

### Learning Result

The Authorization Server can be tested independently from the Resource Server.

This reinforces:

```text
Protocol Role
    ≠
Other Service Responsibilities
```

---

## Step 6 — Identify the Resource Server

The existing FastAPI application remains the Resource Server.

```text
Resource Server
    :8000
```

It exposes:

```http
GET /health
GET /api/profile
```

The `/api/profile` endpoint represents the protected resource boundary for this Lab.

### Learning Result

```text
Resource Server
    =
Component responsible for protecting and serving resources
```

---

## Step 7 — Verify the Resource Server

Verify:

```text
GET http://127.0.0.1:8000/health
```

and:

```text
GET http://127.0.0.1:8000/api/profile
```

Expected profile:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

### Learning Result

The Resource Server is independently reachable and exposes a concrete protected-resource endpoint.

---

## Step 8 — Verify the React Client → Resource Server Path

Start the React Client and open:

```text
http://localhost:5173
```

The Client requests:

```http
GET http://127.0.0.1:8000/api/profile
```

and renders the returned data.

The observed UI was:

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

The current application relationship is:

```text
User
  ↓
Browser
  ↓
React Client
  ↓
Resource Server
```

This is application communication, not yet an OAuth authorization flow.

---

## Step 9 — Verify That the Authorization Server Is Not Yet in the Request Path

At the current Lab stage, the React Client does not initiate an Authorization Request.

Therefore the request path remains:

```text
React Client
     │
     │ GET /api/profile
     ▼
Resource Server :8000
```

There is no:

```text
React Client
     │
     │ GET /authorize
     ▼
Authorization Server :9000
```

yet.

### Learning Result

This is a critical distinction:

```text
Authorization Server exists
    ≠
OAuth authorization flow has been implemented
```

The protocol interaction will begin in the next Lab.

---

## Step 10 — Identify All Roles

Map the running system:

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

### Learning Result

The abstract role model is now mapped onto concrete software.

---

## Step 11 — Same Framework Experiment

Both backend components use FastAPI.

```text
FastAPI :9000
    → Authorization Server

FastAPI :8000
    → Resource Server
```

This does not make them the same OAuth role.

### Learning Result

```text
Framework
    ≠
OAuth Role
```

Role is determined by protocol responsibility.

---

## Step 12 — Same Server Experiment

OAuth does not require the Authorization Server and Resource Server to run on different physical servers.

A valid conceptual deployment can be:

```text
Single Server
    ├── Authorization Server responsibilities
    └── Resource Server responsibilities
```

They may also be deployed independently:

```text
Authorization Server :9000
Resource Server      :8000
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

A single application process can theoretically expose both responsibilities:

```text
Single Application
    ├── Authorization Endpoint
    ├── Token Endpoint
    └── Protected Resource endpoints
```

The responsibilities remain logically distinct even though they share one process.

### Learning Result

```text
Process Boundary
    ≠
OAuth Role Boundary
```

---

## Step 14 — Same Database Experiment

OAuth does not require separate databases for the Authorization Server and Resource Server.

A deployment may use:

```text
Authorization Server ─┐
                      ├── PostgreSQL
Resource Server ──────┘
```

or separate persistence systems.

The database topology is an application architecture decision.

### Learning Result

```text
Database Boundary
    ≠
OAuth Role Boundary
```

---

## Step 15 — Client Type Context

The React Client runs in a browser.

For OAuth security reasoning, this is treated as a public Client because code delivered to the browser cannot safely keep a provisioned client credential secret.

However, Lab 02 does not yet implement the behavioral consequences of that Client classification.

Those consequences become important in later Labs, particularly around Authorization Request, Token Exchange, Refresh Token protection, and PKCE.

### Learning Result

```text
Client
   ↓
Public Client
```

is a classification of the Client's security properties, not another OAuth role.

---

# 7. Final Architecture

The Lab now contains three independently identifiable software components:

```text
                    Resource Owner
                          │
                          ▼
                       Browser
                    (User Agent)
                          │
                          ▼
                   ┌───────────┐
                   │   React   │
                   │   Client  │
                   └─────┬─────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              │                     │
              ▼                     ▼
      ┌──────────────┐      ┌──────────────┐
      │ Authorization│      │   Resource   │
      │    Server    │      │    Server    │
      │  FastAPI     │      │   FastAPI    │
      │   :9000      │      │    :8000     │
      └──────────────┘      └──────┬───────┘
                                    │
                                    ▼
                             Protected Resource
```

Current request path:

```text
Browser
   ↓
React Client
   ↓
Resource Server
```

Deferred OAuth path:

```text
React Client
   ↓
Authorization Request
   ↓
Authorization Server
```

---

# 8. Execution Results

## Authorization Server

Observed:

```text
GET /health                     200 OK
GET /docs                       200 OK
GET /openapi.json               200 OK
```

Automated tests:

```text
2 passed
```

The test suite verified:

```text
Health endpoint                 PASS
Unknown route                   PASS
```

---

## Resource Server

The Resource Server remained operational from the Lab 01 implementation and was used successfully by the Lab 02 Client.

Observed:

```text
GET /health                     200 OK
GET /api/profile                200 OK
```

The profile response was:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

---

## React Client

The React Client rendered successfully and displayed the Resource Server response.

Observed:

```text
OAuth 2.0 Identity Lab
Role: OAuth Client

Resource Server Response
ID: demo-user
Display Name: Lab User
Resource: protected
```

---

## Client → Resource Server Integration

The Client successfully communicated with:

```text
http://127.0.0.1:8000/api/profile
```

and rendered the returned response.

The initial browser integration required CORS configuration because:

```text
React origin
http://localhost:5173

Resource Server origin
http://127.0.0.1:8000
```

are different origins.

The Resource Server was configured to explicitly allow the React development origin.

Final integration:

```text
PASS
```

---

# 9. Acceptance Criteria

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
[x] Client Type is understood as a classification rather than a role.
[x] Same-framework distinction is understood.
[x] Same-server distinction is understood.
[x] Same-process distinction is understood.
[x] Same-database distinction is understood.
[x] Authorization Request is intentionally deferred.
[x] Authorization Code is intentionally deferred.
[x] Token Exchange is intentionally deferred.
[x] Access Token is intentionally deferred.
[x] PKCE is intentionally deferred.
```

---

# 10. What We Learned

## Role Mapping

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

## Responsibility Mapping

```text
Resource Owner
    → Can grant access

Client
    → Requests access

Authorization Server
    → Handles authorization and token issuance

Resource Server
    → Protects resources
```

## Architecture Mapping

```text
Role
    ≠
Framework

Role
    ≠
Process

Role
    ≠
Physical Server

Role
    ≠
Database
```

This is the central learning result of Lab 02.

---

# 11. Important Boundary

The current Lab does **not** implement a complete OAuth flow.

Currently:

```text
React Client
      ↓
Resource Server
```

The Authorization Server is present but not yet part of the Client's request flow.

In the next stage, we will introduce:

```text
React Client
      ↓
Authorization Request
      ↓
Authorization Server
```

This begins the actual OAuth protocol interaction.

---

# 12. Relation to Future Labs

Lab 02 establishes the participants.

The next Labs establish their protocol interactions.

```text
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

The current components are therefore foundations for the next Labs rather than disposable demonstrations.

---

# 13. Standards Basis

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Defines the four primary OAuth roles and the foundational
relationship between the Client, Authorization Server,
and Resource Server.


RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Provides the current security interpretation of OAuth 2.0,
including guidance relevant to Clients, Authorization Servers,
Resource Servers, authorization-code protection, PKCE,
redirect URI handling, and token security.
```

The detailed protocol requirements are intentionally deferred to the Labs where those protocol interactions are implemented.

---

# 14. Completion Status

```text
Lab 02 — OAuth 2.0 Roles

Client
    ✅ Complete

Authorization Server
    ✅ Complete for role demonstration

Resource Server
    ✅ Complete

Role Mapping
    ✅ Complete

Independent Service Verification
    ✅ Complete

Client → Resource Server
    ✅ Complete

Authorization Server → Client OAuth Flow
    ⏳ Deferred to Lab 03

Authorization Request
    ⏳ Deferred to Lab 03

Authorization Code
    ⏳ Deferred to Lab 04

Token Exchange
    ⏳ Deferred to Lab 05

Access Token
    ⏳ Deferred to Lab 06

Refresh Token
    ⏳ Deferred to Lab 07

PKCE
    ⏳ Deferred to Lab 08
```

**Final Result: PASS**

Lab 02 successfully transformed the OAuth 2.0 role model into concrete, independently identifiable application components while preserving the distinction between protocol responsibilities and deployment architecture.
