# Lecture 01 — OAuth 2.0 Overview

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Basic understanding of HTTP, web applications, and client-server communication

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain the problem OAuth 2.0 is designed to solve.
* Distinguish delegated authorization from user authentication.
* Identify the four roles defined by OAuth 2.0.
* Explain the high-level relationship between the Client, Resource Owner, Authorization Server, and Resource Server.
* Understand the purpose of an authorization grant and an access token.
* Distinguish the Authorization Endpoint from the Token Endpoint.
* Explain why OAuth 2.0 is a framework rather than one fixed implementation.
* Understand the difference between an OAuth standard and a provider's implementation.
* Recognize the modern security guidance that must be considered alongside the original OAuth 2.0 specification.

---

# 2. The Problem OAuth 2.0 Solves

Imagine a user wants an application to access some protected information from another service.

A naive design could look like this:

```text
User
  │
  │ Gives username + password
  ▼
Application
  │
  │ Uses user's credentials
  ▼
Protected Service
```

This creates a serious security problem.

The application now possesses credentials that may provide much broader access than the application actually needs.

OAuth 2.0 introduces a different model:

```text
User
  │
  │ Authorizes
  ▼
Authorization Server
  │
  │ Issues authorization credential
  ▼
Client
  │
  │ Access Token
  ▼
Resource Server
  │
  │ Protected Resource
  ▼
Client
```

The application does not need to receive the user's password merely to obtain delegated access.

Instead, the authorization is represented by an OAuth credential.

RFC 6749 defines OAuth 2.0 as a framework that enables a third-party application to obtain limited access to an HTTP service on behalf of a Resource Owner, or on its own behalf.

---

# 3. OAuth 2.0 Is an Authorization Framework

The most important concept to establish first is:

```text
OAuth 2.0
    =
Authorization
```

OAuth answers questions such as:

```text
What access has been granted?

For which Client?

To which protected resource?

Under which authorization conditions?
```

OAuth does **not** itself define a standardized user authentication protocol.

Therefore:

```text
OAuth 2.0
    ↓
Authorization
```

is different from:

```text
OpenID Connect
    ↓
Authentication / Identity
```

OpenID Connect later builds an identity layer on top of OAuth 2.0.

This distinction must remain clear throughout the rest of the learning track.

---

# 4. The Four OAuth Roles

OAuth 2.0 defines four main roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The complete relationship is:

```text
Resource Owner
      │
      │ Grants access
      ▼
Client
      │
      │ Obtains authorization
      ▼
Authorization Server
      │
      │ Issues Access Token
      ▼
Resource Server
      │
      │ Serves Protected Resource
      ▼
Client
```

Each role represents a responsibility in the protocol.

---

# 5. Resource Owner

The **Resource Owner** is the entity capable of granting access to the protected resource.

In many applications:

```text
Resource Owner
      =
User
```

For example:

```text
User
  ↓
Owns or controls
  ↓
Protected Data
```

The important part of the definition is not that the Resource Owner must be a human.

The important part is that the entity has the authority to grant access.

---

# 6. Client

The **Client** is the application requesting access to a protected resource.

Examples include:

```text
Web Application
Mobile Application
Desktop Application
Backend Service
```

The Client does not automatically own the protected resource.

It is requesting access that has been delegated to it.

Conceptually:

```text
Client
   │
   │ "I need authorized access."
   ▼
Authorization Server
```

---

# 7. Authorization Server

The **Authorization Server** is responsible for obtaining authorization and issuing access tokens after the applicable authorization process succeeds.

Conceptually:

```text
Authorization Server
        │
        ├── Authorization Endpoint
        │
        └── Token Endpoint
```

The Authorization Server is the party responsible for the authorization decision and token issuance.

It may also perform user authentication as part of its authorization process, but authentication itself is not what OAuth 2.0 standardizes as an identity protocol.

---

# 8. Resource Server

The **Resource Server** hosts the protected resource.

For example:

```text
Protected API
```

The Client presents an Access Token to the Resource Server:

```text
Client
  │
  │ Access Token
  ▼
Resource Server
  │
  ▼
Protected Resource
```

The Resource Server is responsible for protecting the resource and applying the authorization rules relevant to the presented credential.

---

# 9. One System Can Perform Multiple Roles

The four roles describe **protocol responsibilities**, not necessarily four separate machines.

For example, one platform could operate both:

```text
Authorization Server
        +
Resource Server
```

The physical deployment might therefore look like:

```text
Identity Platform
      │
      ├── Authorization Service
      │
      └── API
```

Even though the same organization operates both components, their protocol responsibilities remain conceptually different.

This separation is important because:

```text
"Should a token be issued?"
```

and:

```text
"Should this protected resource be returned?"
```

are different security decisions.

---

# 10. The High-Level OAuth Flow

At the highest level, OAuth can be understood as:

```text
1. Client needs access.

2. Resource Owner authorizes access.

3. Authorization Server processes the authorization.

4. Client obtains an authorization grant.

5. Client exchanges the applicable grant for an Access Token.

6. Client presents the Access Token to the Resource Server.

7. Resource Server evaluates the request.

8. Protected Resource is returned if authorization succeeds.
```

The core sequence is:

```text
Authorization
      ↓
Authorization Grant
      ↓
Access Token
      ↓
Protected Resource
```

The exact mechanics depend on the grant type, client type, and applicable extensions.

---

# 11. Authorization Grant vs Access Token

These two concepts should not be treated as the same thing.

An **authorization grant** represents a way for the Client to obtain an Access Token.

An **Access Token** is the credential used to access protected resources.

Conceptually:

```text
Authorization Grant
        │
        │ exchanged at Token Endpoint
        ▼
Access Token
        │
        │ presented to Resource Server
        ▼
Protected Resource
```

In the Authorization Code Grant, the authorization code is the authorization grant used at the Token Endpoint.

Therefore:

```text
Authorization Code
      ≠
Access Token
```

This distinction becomes central in the next lectures.

---

# 12. Authorization Endpoint vs Token Endpoint

OAuth commonly separates the authorization interaction from token issuance.

## Authorization Endpoint

The Client directs the Resource Owner's user agent to the Authorization Endpoint.

```text
Client
  │
  │ Authorization Request
  ▼
User Agent
  │
  ▼
Authorization Endpoint
```

The Resource Owner can then interact with the Authorization Server.

---

## Token Endpoint

The Client communicates with the Token Endpoint to obtain an Access Token.

```text
Client
  │
  │ Token Request
  ▼
Token Endpoint
  │
  ▼
Access Token
```

The conceptual distinction is:

```text
Authorization Endpoint
    =
Authorization interaction

Token Endpoint
    =
Token issuance
```

---

# 13. Why the User Agent Participates

OAuth authorization is often mediated by the user's browser.

Conceptually:

```text
Client
  │
  │ Authorization Request
  ▼
Browser
  │
  │ User interaction
  ▼
Authorization Server
```

This means the Client does not need to collect the user's Authorization Server credentials itself.

The exact architecture depends on the client type.

For native applications, RFC 8252 specifies the use of an external user-agent, primarily the user's browser.

For browser-based applications, the current dedicated BCP is now RFC 10017, which provides additional architectural and security guidance beyond the general OAuth framework.

Those client-specific architectures will be studied separately rather than mixed into this foundational overview.

---

# 14. OAuth Does Not Define One Fixed Implementation

OAuth 2.0 is a framework.

That means different deployments can differ in:

```text
Client type
Client authentication
Token format
Authorization policies
Protected resources
Extensions
Security mechanisms
Deployment architecture
```

The protocol defines relationships and rules while allowing different implementations.

For example, an Access Token might be represented as:

```text
Opaque Token
```

or:

```text
JWT
```

depending on the authorization system.

Therefore:

```text
OAuth
    ≠
One specific token format
```

and:

```text
OAuth
    ≠
One specific provider
```

---

# 15. Standard vs Provider Implementation

This distinction is fundamental to this repository.

The learning sequence is:

```text
OAuth Standard
      ↓
Core Theory
      ↓
Production-oriented Lab
      ↓
Provider Implementation
```

For example:

```text
Standard:
OAuth Authorization Code Grant

Provider:
Microsoft Entra ID

Question:
How does Microsoft implement the standard?
```

The correct direction is:

```text
Standard
   ↓
Implementation
```

not:

```text
Provider
   ↓
Definition of the Standard
```

This allows the same knowledge to transfer to other providers later.

---

# 16. OAuth Is Not "Login"

A common simplification is:

```text
OAuth
 =
Login with another account
```

That is not precise.

OAuth defines delegated authorization.

A user may authorize a Client to access:

```text
Calendar Data
Files
Messages
Profile Data
Business APIs
```

without OAuth itself defining how the Client establishes the user's identity.

For standardized identity and authentication information, OpenID Connect adds an identity layer on top of OAuth 2.0.

Therefore keep these concepts separate:

```text
OAuth 2.0
    ↓
"May this Client access this protected resource?"

OpenID Connect
    ↓
"Who authenticated?"
```

---

# 17. OAuth and OpenID Connect

The relationship can be visualized as:

```text
OpenID Connect
       │
       │ builds on
       ▼
   OAuth 2.0
       │
       ├── Authorization
       ├── Access Tokens
       └── Protected Resources
```

OpenID Connect adds concepts such as:

```text
ID Token
Issuer
Subject
UserInfo
Nonce
```

Those concepts belong to the OIDC layer and will be introduced later.

---

# 18. Why OAuth Requires Security Thinking

OAuth is a security protocol.

A flow that successfully produces a token is not automatically a secure implementation.

For example:

```text
Flow works
   ≠
Flow is secure
```

Security depends on questions such as:

```text
Can an attacker steal the authorization code?

Can an attacker alter the redirect?

Can a token be replayed?

Can a token intended for one resource be used at another?

Can a Client be impersonated?

Can an attacker confuse the Client about which authorization server it is talking to?
```

The original OAuth 2.0 specification contains foundational security considerations, but current deployments must also consider newer security guidance.

RFC 9700, published in January 2025, is the current OAuth 2.0 Security Best Current Practice. It updates and extends the security advice from RFC 6749, RFC 6750, and RFC 6819 and deprecates less-secure modes of operation.

---

# 19. Modern OAuth Security Baseline

Current OAuth security guidance places strong emphasis on mechanisms such as:

```text
PKCE
Secure Redirect URI Handling
CSRF Protection
Authorization-Code Protection
Mix-Up Attack Protection
Secure Token Handling
```

These mechanisms are not arbitrary implementation preferences.

They address concrete threats against the protocol.

For example:

```text
Authorization Code
        │
        │ intercepted
        ▼
     Attacker
        │
        │ tries token exchange
        ▼
     PKCE
        │
        ▼
    Verification
        │
        ▼
     Reject
```

This is one reason the modern learning path should study the protocol and the security properties together.

RFC 9700 explicitly recommends upgrading implementations to its current practices as feasible.

---

# 20. Current OAuth Landscape

It is useful to understand how the specifications relate to one another.

The foundational specification is:

```text
RFC 6749
OAuth 2.0 Authorization Framework
```

The current security guidance is:

```text
RFC 9700
Best Current Practice for OAuth 2.0 Security
```

Additional specifications address particular environments or capabilities, such as:

```text
RFC 7636
PKCE

RFC 8252
Native Applications

RFC 8414
Authorization Server Metadata
```

For browser-based applications, the IETF has also published:

```text
RFC 10017
OAuth 2.0 for Browser-Based Applications
```

in August 2026. It provides specialized guidance for applications executing in browsers and builds on the security recommendations in RFC 9700.

Therefore the modern picture is not:

```text
One RFC
    ↓
Complete OAuth knowledge
```

but:

```text
RFC 6749
    +
Applicable Extensions
    +
Current Best Current Practice
    ↓
Modern OAuth Implementation
```

---

# 21. OAuth 2.1 and the Current Specification Landscape

You may encounter the term:

```text
OAuth 2.1
```

during your studies.

It is important not to confuse a developing specification with a published replacement standard.

RFC 9700 states that OAuth 2.1 is under development and is intended to incorporate the security recommendations from the current BCP.

For this learning track, the correct approach is therefore:

```text
RFC 6749
    ↓
Understand the OAuth 2.0 foundation

RFC 9700
    ↓
Apply current security guidance

Specific RFCs / BCPs
    ↓
Study the relevant extension or deployment
```

We will not treat "OAuth 2.1" as though it were already a finalized published replacement for RFC 6749.

---

# 22. The Core Mental Model

At this stage, do not memorize every parameter.

Understand the purpose of the protocol:

```text
                    WHO?

Resource Owner
      │
      │ Grants authorization
      ▼
Client
      │
      │ Requests authorization
      ▼
Authorization Server
      │
      │ Issues Access Token
      ▼
Client
      │
      │ Presents Access Token
      ▼
Resource Server
      │
      │ Evaluates authorization
      ▼
Protected Resource
```

The conceptual journey is:

```text
Need Access
     ↓
Obtain Authorization
     ↓
Obtain Access Token
     ↓
Present Access Token
     ↓
Access Protected Resource
```

That is the foundation on which the rest of OAuth is built.

---

# 23. What You Should Not Assume

After this lecture, avoid these assumptions:

```text
OAuth = Login
```

```text
Access Token = JWT
```

```text
Authorization Server = Resource Server
```

```text
Authorization Code = Access Token
```

```text
Client = User
```

```text
OAuth = One Provider's Implementation
```

```text
Working Flow = Secure Flow
```

Each of these shortcuts hides an important distinction.

---

# 24. Production Perspective

A production OAuth implementation must consider more than:

```text
"Can I obtain a token?"
```

It must also consider:

```text
Who is the Client?

Which Authorization Server is trusted?

Which redirect URI is allowed?

Which authorization grant is being used?

How is the authorization code protected?

How is the token protected?

Which Resource Server is the token intended for?

How is the token validated?

What happens when validation fails?
```

The exact answers depend on the architecture and client type.

The purpose of this learning track is to build those answers progressively rather than hiding them behind a provider-specific SDK.

---

# 25. Knowledge Check

### Question 1

What problem does OAuth 2.0 solve?

---

### Question 2

What is the difference between authentication and authorization?

---

### Question 3

What are the four OAuth 2.0 roles?

---

### Question 4

What is the responsibility of the Authorization Server?

---

### Question 5

What is the responsibility of the Resource Server?

---

### Question 6

What is the difference between an authorization grant and an Access Token?

---

### Question 7

What is the difference between the Authorization Endpoint and the Token Endpoint?

---

### Question 8

Why is OAuth 2.0 called a framework rather than one fixed implementation?

---

### Question 9

Why is:

```text
OAuth = Login
```

an inaccurate mental model?

---

### Question 10

Why should a modern OAuth implementation consider RFC 9700 in addition to RFC 6749?

---

# 26. Lecture Summary

OAuth 2.0 is an **authorization framework** designed to allow a Client to obtain limited access to protected resources without requiring the Resource Owner to hand the Client its credentials.

The four core roles are:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The high-level relationship is:

```text
Resource Owner
      ↓
Authorization
      ↓
Client
      ↓
Authorization Server
      ↓
Access Token
      ↓
Resource Server
      ↓
Protected Resource
```

The most important distinctions are:

```text
Authorization
    ≠
Authentication

Authorization Grant
    ≠
Access Token

Authorization Server
    ≠
Resource Server

OAuth 2.0
    ≠
OpenID Connect

OAuth Standard
    ≠
Provider Implementation
```

The foundational protocol comes from RFC 6749, while modern security practice must also account for RFC 9700 and other applicable specifications.

The central mental model to retain is:

```text
OAuth 2.0
    ↓
Delegated Authorization
    ↓
Authorization Grant
    ↓
Access Token
    ↓
Protected Resource
```

This foundation will be used by the next lectures to examine the individual protocol interactions in detail.

---

# 27. References

```text
PRIMARY / FOUNDATIONAL

RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Status:
Foundational OAuth 2.0 specification.

Important update relationship:
Updated by RFC 8252, RFC 8996, and RFC 9700.


CURRENT SECURITY GUIDANCE

RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Status:
Best Current Practice (BCP 240).

Role in this lecture:
Current security baseline for understanding modern OAuth
implementations.


NATIVE APPLICATIONS

RFC 8252 — OAuth 2.0 for Native Apps
https://www.rfc-editor.org/rfc/rfc8252.html

Status:
Best Current Practice (BCP 212).

Role in this lecture:
Introduces deployment-specific considerations for native
applications and external user-agent use.


AUTHORIZATION SERVER METADATA

RFC 8414 — OAuth 2.0 Authorization Server Metadata
https://www.rfc-editor.org/rfc/rfc8414.html

Role in the learning track:
Standardized Authorization Server metadata and discovery
concepts.


BROWSER-BASED APPLICATIONS

RFC 10017 — OAuth 2.0 for Browser-Based Applications
https://www.rfc-editor.org/rfc/rfc10017.html

Status:
Best Current Practice.

Published:
August 2026.

Role in the learning track:
Current deployment-specific security and architecture guidance
for browser-based OAuth applications.

This lecture only introduces its existence because detailed
browser architecture belongs to a later topic.


PKCE

RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html

Role in the learning track:
Defines PKCE, which will be studied separately.


SPECIFICATION LANDSCAPE

RFC 6749
    ↓
OAuth 2.0 foundation

RFC 9700
    ↓
Current OAuth security BCP

RFC 7636
    ↓
PKCE

RFC 8252
    ↓
Native application guidance

RFC 8414
    ↓
Authorization Server Metadata

RFC 10017
    ↓
Browser-based application guidance


IMPORTANT CURRENT-STATUS NOTE

OAuth 2.1 is still described by RFC 9700 as under development.

Therefore this lecture does not present OAuth 2.1 as a finalized
replacement standard for RFC 6749.
```

---

# 28. Source Currency / Update Check

```text
RFC 6749
    │
    ├── Updated by RFC 8252
    ├── Updated by RFC 8996
    └── Updated by RFC 9700
          │
          └── Current OAuth Security BCP

RFC 7636
    │
    └── PKCE specification

RFC 8252
    │
    └── Native application BCP

RFC 8414
    │
    └── Authorization Server Metadata

RFC 10017
    │
    └── Current browser-based application BCP
        (published August 2026)

OAuth 2.1
    │
    └── Still under development
```

The lecture therefore uses RFC 6749 as the foundational protocol source while incorporating the current applicable security and deployment guidance rather than treating the 2012 specification in isolation.
