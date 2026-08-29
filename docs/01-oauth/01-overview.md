# Lecture 01 — OAuth 2.0 Overview

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Basic understanding of HTTP, web applications, and client-server communication

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain the problem OAuth 2.0 is designed to solve.
* Distinguish delegated authorization from user authentication.
* Identify the four OAuth roles.
* Explain the relationship between the Client, Resource Owner, Authorization Server, and Resource Server.
* Distinguish an authorization grant from an Access Token.
* Distinguish the Authorization Endpoint from the Token Endpoint.
* Understand OAuth 2.0 as a framework rather than one fixed implementation.
* Distinguish provider-neutral protocol concepts from provider-specific implementations.
* Recognize the modern security baseline that applies to OAuth 2.0 implementations.

---

# 2. The Problem OAuth 2.0 Solves

Suppose a user wants an application to access protected data held by another service.

A weak design would require the application to collect the user's service credentials:

```text
User
  │
  │ username + password
  ▼
Application
  │
  │ uses user's credentials
  ▼
Protected Service
```

This gives the application credentials that may provide more authority than it actually needs.

OAuth 2.0 introduces delegated authorization:

```text
Resource Owner
      │
      │ authorizes
      ▼
Authorization Server
      │
      │ authorization credential
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

The Client can obtain limited access without receiving the Resource Owner's password.

RFC 6749 defines OAuth 2.0 as a framework enabling a third-party application to obtain limited access to an HTTP service on behalf of a Resource Owner, or on its own behalf.

---

# 3. OAuth 2.0 Is About Authorization

The first distinction to internalize is:

```text
OAuth 2.0
    =
Authorization
```

OAuth provides a framework for obtaining and using authorization to protected resources.

It does not by itself define a standardized identity protocol that tells the Client who authenticated.

Therefore:

```text
OAuth 2.0
    ↓
Delegated Authorization
```

is different from:

```text
OpenID Connect
    ↓
Authentication / Identity
```

OpenID Connect builds an identity layer on top of OAuth 2.0.

---

# 4. The Four OAuth Roles

OAuth 2.0 defines four primary roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

Their relationship is:

```text
Resource Owner
      │
      │ grants authorization
      ▼
Client
      │
      │ obtains authorization
      ▼
Authorization Server
      │
      │ issues Access Token
      ▼
Resource Server
      │
      │ serves Protected Resource
      ▼
Client
```

These are protocol roles. They do not require four separate physical servers.

---

# 5. Resource Owner

The **Resource Owner** is the entity capable of granting access to a protected resource.

In a user-delegated application this is commonly:

```text
Resource Owner = User
```

The definition is based on authority over the protected resource, not on whether the Resource Owner is necessarily a human.

---

# 6. Client

The **Client** is the application requesting access to a protected resource.

Examples include:

```text
Web Application
Mobile Application
Desktop Application
Backend Application
```

The Client is requesting delegated access. It is not automatically the owner of the protected resource.

---

# 7. Authorization Server

The **Authorization Server** is the server that issues Access Tokens after successfully processing the applicable authorization grant.

It commonly exposes protocol endpoints such as:

```text
Authorization Endpoint
Token Endpoint
```

It may also authenticate the Resource Owner as part of its authorization process, but user authentication is not itself the identity layer standardized by OAuth 2.0.

---

# 8. Resource Server

The **Resource Server** hosts protected resources, such as a protected API.

The Client presents an Access Token when requesting the protected resource:

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

The Resource Server applies the authorization rules relevant to the request.

---

# 9. Roles Are Logical, Not Necessarily Physical

A single deployment can perform multiple OAuth roles.

For example:

```text
Platform
  ├── Authorization Service
  └── Protected API
```

The platform therefore acts as both an Authorization Server and a Resource Server.

The distinction still matters because:

```text
Should authorization be granted?
```

and:

```text
Should this resource request be allowed?
```

are different security decisions.

---

# 10. The High-Level OAuth Flow

The complete protocol can be summarized as:

```text
1. Client needs access.
2. Resource Owner authorizes the Client.
3. Authorization Server processes the authorization.
4. Client obtains an authorization grant.
5. Client exchanges the applicable grant for an Access Token.
6. Client presents the Access Token to the Resource Server.
7. Resource Server evaluates the request.
8. Protected Resource is returned when authorization succeeds.
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

The exact protocol messages and security mechanisms depend on the selected OAuth flow and deployment profile.

---

# 11. Authorization Grant vs Access Token

These concepts are related but different.

An **authorization grant** is a credential or representation of authorization that the Client uses to obtain an Access Token.

An **Access Token** is the credential used to access a protected resource.

```text
Authorization Grant
        │
        │ Token Endpoint
        ▼
Access Token
        │
        │ Resource Request
        ▼
Protected Resource
```

In the Authorization Code Grant:

```text
Authorization Code
      ↓
Authorization Grant
      ↓
Token Endpoint
      ↓
Access Token
```

Therefore:

```text
Authorization Code ≠ Access Token
```

---

# 12. Authorization Endpoint vs Token Endpoint

OAuth commonly separates authorization interaction from token issuance.

### Authorization Endpoint

The Client directs the user agent to the Authorization Endpoint:

```text
Client
  ↓
User Agent
  ↓
Authorization Endpoint
```

The Resource Owner can interact with the Authorization Server there.

### Token Endpoint

The Client sends a token request to the Token Endpoint:

```text
Client
  ↓
Token Endpoint
  ↓
Access Token
```

Therefore:

```text
Authorization Endpoint
    = Authorization interaction

Token Endpoint
    = Token issuance
```

---

# 13. Why the User Agent Participates

Authorization is frequently mediated by the user's browser or another user agent.

```text
Client
  │
  │ Authorization Request
  ▼
User Agent
  │
  │ User interaction
  ▼
Authorization Server
```

This allows the Authorization Server to handle the authorization interaction rather than requiring the Client to collect the user's Authorization Server credentials.

The exact architecture depends on the client type. Native applications have dedicated guidance in RFC 8252, while browser-based applications now have dedicated current guidance in RFC 10017.

---

# 14. OAuth 2.0 Is a Framework

OAuth 2.0 is not one fixed application architecture.

Implementations can differ in:

```text
Client type
Client authentication
Authorization grant
Token format
Resource Server architecture
Security mechanisms
Extensions
Deployment model
```

For example, an Access Token may be opaque or may use JWT as its representation.

Therefore:

```text
Access Token ≠ JWT
```

A JWT is a token representation format, while an Access Token is an OAuth authorization credential.

---

# 15. OAuth Standard vs Provider Implementation

This repository intentionally separates the two.

The learning direction is:

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
Authorization Code Grant

Provider:
Microsoft Entra ID

Question:
How does this provider implement the standard?
```

The Provider is therefore an implementation to study, not the definition of OAuth itself.

---

# 16. OAuth Is Not "Login"

A common shortcut is:

```text
OAuth = Login
```

That is inaccurate.

OAuth is fundamentally about delegated authorization.

A Client may be authorized to access files, calendar data, messages, or business APIs without OAuth itself standardizing the identity information shown to the Client.

OpenID Connect provides that identity layer.

```text
OAuth 2.0
    ↓
"Can this Client access this protected resource?"

OpenID Connect
    ↓
"Who authenticated?"
```

---

# 17. Modern OAuth Security Baseline

The original OAuth 2.0 specification remains foundational, but its security guidance should not be read in isolation.

RFC 9700 is the current OAuth 2.0 Security Best Current Practice and updates or extends the security interpretation of earlier OAuth specifications.

Modern implementations should consider protections including:

```text
PKCE
Secure Redirect URI Handling
CSRF Protection
Authorization-Code Protection
Mix-Up Attack Protection
Secure Token Handling
```

The important lesson is:

```text
Flow works
   ≠
Flow is secure
```

Security controls must be selected according to the client type, threat model, and applicable current guidance.

---

# 18. Current Guidance for Browser-Based Applications

A major update to the OAuth landscape is RFC 10017, **OAuth 2.0 for Browser-Based Applications**.

It provides deployment-specific guidance for OAuth Clients executing in browsers and builds on the current OAuth security baseline.

For browser-based public clients, the modern baseline is:

```text
Authorization Code Grant
        +
PKCE
```

The specification also addresses browser-specific threats such as malicious JavaScript and discusses architectures including a Backend for Frontend (BFF), token storage choices, sender-constrained tokens, and authorization-server mix-up mitigation.

These details will be studied in the browser/client-architecture material; this overview establishes that browser applications have their own current security guidance and should not be designed from the historical Implicit Grant model.

---

# 19. Resource and Audience Considerations

Modern OAuth deployments may involve multiple protected resources.

A Client should not assume that a token issued for one resource is automatically valid at another.

RFC 8707 defines the OAuth `resource` parameter for explicitly identifying the protected resource for which authorization is requested. Current OAuth security guidance also emphasizes restricting token use to the intended resource.

This becomes important later when we study Access Tokens and Resource Servers.

---

# 20. Production Perspective

A production OAuth implementation must answer more than:

```text
"Can I get a token?"
```

It should also answer:

```text
Who is the Client?
Which Authorization Server is trusted?
Which redirect URI is valid?
Which grant is being used?
How is the authorization code protected?
How is the token protected?
Which resource is the token intended for?
How is the token validated?
What happens when validation fails?
```

The Labs in this repository should therefore implement security properties, not merely demonstrate that a token can be obtained.

---

# 21. Core Mental Model

At this stage, remember the protocol rather than memorizing every parameter.

```text
Resource Owner
      │
      │ grants authorization
      ▼
Client
      │
      │ authorization request
      ▼
Authorization Server
      │
      │ authorization grant
      ▼
Client
      │
      │ token request
      ▼
Authorization Server
      │
      │ Access Token
      ▼
Client
      │
      │ protected-resource request
      ▼
Resource Server
      │
      │ Protected Resource
      ▼
Client
```

The fundamental sequence is:

```text
Request Authorization
        ↓
Obtain Authorization Grant
        ↓
Exchange for Access Token
        ↓
Present Access Token
        ↓
Access Protected Resource
```

---

# 22. What You Should Not Assume

Do not carry these shortcuts into later lectures:

```text
OAuth = Login
```

```text
Access Token = JWT
```

```text
Authorization Code = Access Token
```

```text
Authorization Server = Resource Server
```

```text
Client = Resource Owner
```

```text
OAuth = One Provider's Implementation
```

```text
A Working Flow = A Secure Flow
```

---

# 23. Knowledge Check

### Question 1
What problem does OAuth 2.0 solve?

### Question 2
What is delegated authorization?

### Question 3
What are the four OAuth roles?

### Question 4
What does the Authorization Server do?

### Question 5
What does the Resource Server do?

### Question 6
What is the difference between an authorization grant and an Access Token?

### Question 7
What is the difference between the Authorization Endpoint and the Token Endpoint?

### Question 8
Why is OAuth 2.0 called a framework?

### Question 9
Why is OAuth not itself a standardized login protocol?

### Question 10
Why should modern OAuth implementations consider RFC 9700 in addition to RFC 6749?

### Question 11
What is the significance of RFC 10017 for browser-based OAuth applications?

### Question 12
Why should provider-specific behavior be treated separately from the OAuth standard?

---

# 24. Lecture Summary

OAuth 2.0 is an **authorization framework** for obtaining limited access to protected resources.

Its four primary roles are:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The high-level flow is:

```text
Resource Owner
      ↓
Authorization
      ↓
Authorization Grant
      ↓
Access Token
      ↓
Protected Resource
```

The most important distinctions are:

```text
Authorization ≠ Authentication
Authorization Grant ≠ Access Token
Authorization Server ≠ Resource Server
OAuth 2.0 ≠ OpenID Connect
OAuth Standard ≠ Provider Implementation
```

RFC 6749 remains the foundational OAuth 2.0 framework, while modern implementations must incorporate applicable newer security and deployment guidance such as RFC 9700 and RFC 10017.

The central mental model is:

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

---

# 25. References

## 25.1 RFC 6749 — The OAuth 2.0 Authorization Framework

**Authority:** Internet Engineering Task Force (IETF)

**Role in this lecture:** Foundational OAuth 2.0 framework.

Official source:

https://www.rfc-editor.org/rfc/rfc6749.html

Defines the core OAuth roles, protocol flow, authorization grants, endpoints, Access Tokens, and scope.

---

## 25.2 RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 240).

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

**Role in this lecture:** Current general OAuth security baseline.

It updates and extends earlier OAuth security guidance and informs the security interpretation of the foundational framework.

---

## 25.3 RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc7636.html

**Role in this lecture:** Foundational specification for PKCE.

---

## 25.4 RFC 8252 — OAuth 2.0 for Native Apps

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice.

Official source:

https://www.rfc-editor.org/rfc/rfc8252.html

**Role in this lecture:** Native application deployment context.

---

## 25.5 RFC 8414 — OAuth 2.0 Authorization Server Metadata

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc8414.html

**Role in this lecture:** Authorization Server metadata and discovery context.

---

## 25.6 RFC 8707 — Resource Indicators for OAuth 2.0

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc8707.html

**Role in this lecture:** Explicit protected-resource targeting.

---

## 25.7 RFC 10017 — OAuth 2.0 for Browser-Based Applications

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice.

**Role in this lecture:** Current browser-based application guidance.

Official source:

https://www.rfc-editor.org/rfc/rfc10017.html

This specification provides deployment-specific guidance for browser-based OAuth applications, including Authorization Code + PKCE, browser threat considerations, token handling, BFF architecture, and mix-up mitigation.

---

# 26. Source Update Analysis Applied to This Lecture

The framework's source-currency rule was applied before writing this lecture.

```text
RFC 6749
    ↓
Foundational OAuth 2.0 framework

RFC 9700
    ↓
Current general OAuth security guidance
    ↓
Affects security interpretation of the framework

RFC 7636
    ↓
PKCE mechanism

RFC 8252
    ↓
Native-app deployment guidance

RFC 8414
    ↓
Authorization Server Metadata

RFC 8707
    ↓
Protected-resource targeting

RFC 10017
    ↓
Current browser-based application guidance
    ↓
Authorization Code + PKCE
Browser threat model
BFF and token-handling architecture
Browser-specific security guidance
```

The newer sources are not included merely to show that they exist. Where they affect the subject of this lecture, their relevant requirements or security guidance have been incorporated directly into the lecture content.

---

# 27. Current Specification Model

For this learning track, OAuth should be studied as a layered specification set rather than as one isolated RFC:

```text
OAuth 2.0 Foundation
        ↓
RFC 6749
        ↓
Applicable Extensions
        ↓
Current Security BCP
RFC 9700
        ↓
Deployment-Specific Guidance
        ↓
Native / Browser / Other Environments
```

OAuth 2.1 may appear in current technical discussions, but this repository does not treat an unfinished or non-final specification as a published replacement unless the standards status changes.

---

# 28. Lab Connection

The practical Labs should turn the model above into a real OAuth transaction.

The goal is not merely:

```text
"I received a token."
```

The goal is to observe and implement:

```text
Authorization Request
        ↓
Authorization Response
        ↓
Authorization Code
        ↓
Token Request
        ↓
Access Token
        ↓
Protected Resource Request
```

and progressively verify the security properties protecting each transition.

The implementation should follow current standards and production-oriented security practices rather than historical toy shortcuts.
