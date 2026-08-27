# OAuth 2.0 & OpenID Connect Identity Lab

> A hands-on laboratory for understanding how modern authentication works from end to end using a real Microsoft Entra ID application.

## Overview

This repository is both a **lecture/reference** and a **hands-on practice lab** for learning OAuth 2.0, OpenID Connect (OIDC), Identity Providers, JWTs, cryptographic signatures, JWKS, token validation, and external identity mapping.

The primary goal is not to simply learn the terminology.

The goal is to **observe the real authentication flow, inspect the actual data returned by an Identity Provider, and use that information to design an application's identity system.**

The lab begins with Microsoft Entra ID and progressively moves from authentication concepts to implementation and database design.

---

## Learning Objectives

By completing this lab, you should be able to explain and demonstrate:

- Authentication vs. Authorization
- OAuth 2.0
- OpenID Connect
- Identity Providers
- Authorization Code Flow
- Authorization Codes
- ID Tokens
- Access Tokens
- JWT structure
- JWT digital signatures
- Issuers (`iss`)
- Subjects (`sub`)
- Audiences (`aud`)
- Microsoft Entra Object IDs (`oid`)
- Tenant IDs (`tid`)
- JWKS
- Public and private signing keys
- Token validation
- Key rotation
- `state`
- `nonce`
- PKCE
- External identity vs. internal application identity
- Mapping an external identity to an internal `user_id`
- Provider-independent identity database design

---

## Core Question

The central question of this lab is:

> **When a user signs in with Microsoft, what exactly does Microsoft give my application, and how can my application safely use that information to identify the user?**

We will answer this by actually running the authentication flow.

```text
User
 │
 │ Sign in
 ▼
Microsoft Entra ID
 │
 │ Authorization Code
 ▼
Your Application
 │
 │ Token Exchange
 ▼
Microsoft Entra ID
 │
 │ ID Token
 ▼
Your Application
 │
 │ Validate Token
 ▼
External Identity
 │
 │ iss + sub
 ▼
user_identities
 │
 │ user_id
 ▼
users
```

---

# Repository Structure

```text
oauth-oidc-identity-lab/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
│
├── docs/
│   │
│   ├── 01-foundations/
│   │   ├── 01-authentication-vs-authorization.md
│   │   ├── 02-oauth-2-overview.md
│   │   ├── 03-openid-connect.md
│   │   └── 04-identity-providers.md
│   │
│   ├── 02-oauth-flow/
│   │   ├── 01-authorization-request.md
│   │   ├── 02-authorization-code.md
│   │   ├── 03-token-exchange.md
│   │   └── 04-complete-flow.md
│   │
│   ├── 03-identity/
│   │   ├── 01-id-token.md
│   │   ├── 02-issuer.md
│   │   ├── 03-subject.md
│   │   ├── 04-object-id.md
│   │   └── 05-external-vs-internal-identity.md
│   │
│   ├── 04-token-security/
│   │   ├── 01-jwt.md
│   │   ├── 02-digital-signatures.md
│   │   ├── 03-jwks.md
│   │   ├── 04-token-validation.md
│   │   └── 05-key-rotation.md
│   │
│   ├── 05-database/
│   │   ├── 01-user-model.md
│   │   ├── 02-user-identities.md
│   │   ├── 03-provider-model.md
│   │   └── 04-identity-mapping.md
│   │
│   └── 06-security/
│       ├── 01-state.md
│       ├── 02-nonce.md
│       ├── 03-pkce.md
│       ├── 04-replay-attacks.md
│       └── 05-common-mistakes.md
│
├── labs/
│   │
│   ├── 01-register-entra-app/
│   │   └── README.md
│   │
│   ├── 02-first-login/
│   │   └── README.md
│   │
│   ├── 03-inspect-id-token/
│   │   └── README.md
│   │
│   ├── 04-identify-user/
│   │   └── README.md
│   │
│   ├── 05-database-mapping/
│   │   └── README.md
│   │
│   ├── 06-token-validation/
│   │   └── README.md
│   │
│   ├── 07-jwks/
│   │   └── README.md
│   │
│   └── 08-security-attacks/
│       └── README.md
│
├── app/
│   │
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   └── database/
│   │   │
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── frontend/
│       ├── index.html
│       └── ...
│
├── database/
│   │
│   ├── migrations/
│   ├── schema.sql
│   └── seed.sql
│
├── diagrams/
│   ├── oauth-flow.md
│   ├── oidc-flow.md
│   ├── identity-mapping.md
│   └── trust-chain.md
│
├── experiments/
│   ├── jwt/
│   ├── jwks/
│   ├── token-validation/
│   └── claims/
│
└── docker-compose.yml
```

---

# Learning Path

The repository is organized as a progression from **concept → observation → experiment → implementation → architecture**.

## Phase 1 — Foundations

Study the basic concepts.

```text
Authentication
      │
      ▼
Authorization
      │
      ▼
OAuth 2.0
      │
      ▼
OpenID Connect
      │
      ▼
Identity Provider
```

Start with:

```text
docs/01-foundations/
```

---

## Phase 2 — Observe the Real Authentication Flow

Create a real Microsoft Entra ID application and connect it to the local application.

```text
Browser
   │
   │ Authorization Request
   ▼
Microsoft Entra ID
   │
   │ User Login
   ▼
Microsoft Entra ID
   │
   │ Authorization Code
   ▼
Your Application
```

Labs:

```text
labs/01-register-entra-app/
labs/02-first-login/
```

---

## Phase 3 — Inspect What Microsoft Actually Gives You

Instead of assuming what an Identity Provider returns, inspect the actual ID Token.

Example claims:

```json
{
  "iss": "https://login.microsoftonline.com/...",
  "sub": "...",
  "aud": "...",
  "oid": "...",
  "tid": "...",
  "name": "...",
  "preferred_username": "..."
}
```

Labs:

```text
labs/03-inspect-id-token/
labs/04-identify-user/
```

The important question is:

> Which value should my application use to identify this external identity?

---

## Phase 4 — Understand the Trust Chain

Investigate how the application knows that an ID Token really came from the expected Identity Provider.

```text
Trusted Issuer
      │
      ▼
OIDC Discovery
      │
      ▼
JWKS
      │
      ▼
Public Signing Key
      │
      ▼
JWT Signature
      │
      ▼
Token Validation
```

Labs:

```text
labs/06-token-validation/
labs/07-jwks/
```

Experiments:

```text
experiments/jwt/
experiments/jwks/
experiments/token-validation/
```

---

## Phase 5 — Design the Database

After observing the real identity information, design the application's identity model.

The target architecture is:

```text
users
  │
  │ user_id
  ▼
user_identities
  │
  │ provider_id
  ▼
identity_providers
```

A simplified identity record might look like:

```text
user_id | issuer | subject
--------|--------|----------------
42      | ...    | ...
```

The fundamental mapping becomes:

```text
External Identity
      │
      │ issuer + subject
      ▼
user_identities
      │
      │ user_id
      ▼
Application User
```

Labs:

```text
labs/05-database-mapping/
```

---

# Security Experiments

Once the normal authentication flow works, intentionally break it.

The objective is to understand **why token validation exists**.

## Experiment 1 — Modify the Subject

Start with a legitimate token.

Change:

```text
sub = legitimate-user
```

to:

```text
sub = another-user
```

without resigning the token.

Expected result:

```text
Invalid signature
```

---

## Experiment 2 — Change the Issuer

Modify:

```text
iss = trusted-provider
```

to:

```text
iss = malicious-provider
```

Expected result:

```text
Invalid issuer
```

---

## Experiment 3 — Change the Audience

Use a validly signed token intended for another application.

Expected result:

```text
Invalid audience
```

This demonstrates why:

```text
Valid Signature
```

does not automatically mean:

```text
Valid Token For My Application
```

---

## Experiment 4 — Expire the Token

Use an expired token.

Expected result:

```text
Token expired
```

---

# Identity Model

The application should separate:

```text
External Identity
```

from:

```text
Internal User
```

For example:

```text
Microsoft Entra
      │
      │ iss + sub
      ▼
user_identities
      │
      │ user_id
      ▼
users
```

This means the application does not need to make Microsoft Entra's identifiers its primary user ID.

The application owns:

```text
users.id
```

while the Identity Provider owns:

```text
iss
sub
```

This separation makes the architecture easier to extend.

---

# Multiple Providers

The long-term goal is to support multiple Identity Providers without redesigning the `users` table.

```text
                    users
                      │
                      ▼
               user_identities
                 │    │    │
                 │    │    │
                 ▼    ▼    ▼
             Microsoft Google GitHub
```

Each external identity can be represented using the same conceptual model:

```text
issuer + subject
```

The application then maps that external identity to its own:

```text
user_id
```

Adding another provider should therefore primarily require a new provider integration rather than a new identity column in the `users` table.

---

# Technology Stack

The initial lab uses:

```text
Backend
Python
FastAPI

Database
PostgreSQL

Authentication
OAuth 2.0
OpenID Connect
JWT

Identity Provider
Microsoft Entra ID

Infrastructure
Docker Compose
```

The technology choices are intentionally simple.

The objective is to understand the authentication architecture rather than introduce unnecessary infrastructure.

---

# Important Security Rules

This repository is an educational lab, but it should still follow good security practices.

Never commit:

```text
Client Secrets
Passwords
Access Tokens
Refresh Tokens
Private Keys
.env files containing secrets
```

Use:

```text
.env
```

for local secrets and commit only:

```text
.env.example
```

Never use an email address as the sole canonical identity key.

Do not trust:

```text
provider
user_id
email
```

sent directly by the browser as proof of identity.

Identity should be derived from a **validated token issued by the trusted Identity Provider**.

---

# Final Architecture

The complete learning target is:

```text
                         ┌─────────────────────┐
                         │ Microsoft Entra ID  │
                         │                     │
                         │ Identity Provider   │
                         └──────────┬──────────┘
                                    │
                         OAuth 2.0 / OIDC
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Your Web App    │
                         │                     │
                         │ Authorization Code  │
                         │ Token Exchange      │
                         │ Token Validation    │
                         └──────────┬──────────┘
                                    │
                               iss + sub
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  user_identities    │
                         │                     │
                         │ issuer              │
                         │ subject             │
                         │ user_id             │
                         └──────────┬──────────┘
                                    │
                                 user_id
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │        users        │
                         │                     │
                         │ Application User    │
                         └─────────────────────┘
```

---

# What This Lab Should Ultimately Answer

By the end of the repository, you should be able to answer these questions from **actual hands-on evidence**:

```text
1. What does Microsoft Entra ID give my application?

2. What is an authorization code?

3. Why does the authorization code change?

4. What is an ID token?

5. What information is inside the ID token?

6. What is `iss`?

7. What is `sub`?

8. What are `oid` and `tid`?

9. How does my application know the token came from Microsoft?

10. Where does Microsoft's public signing key come from?

11. How does JWT signature verification work?

12. Why can't an attacker simply create their own token?

13. Why should email not be the primary identity key?

14. How does an external Microsoft identity become my application's `user_id`?

15. How can the same database architecture support multiple providers?

16. What happens when an Identity Provider rotates its signing keys?
```

---

## License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for details.

---

## Disclaimer

This repository is intended for **educational and experimental purposes**.

Do not use the simplified implementations from the early laboratory exercises as production authentication infrastructure without applying appropriate security reviews and production-grade libraries/configuration.
