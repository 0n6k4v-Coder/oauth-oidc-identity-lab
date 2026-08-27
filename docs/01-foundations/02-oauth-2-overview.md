# Lecture 02 — OAuth 2.0 Overview

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Lecture 01 — Authentication vs Authorization

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain the problem OAuth 2.0 was designed to solve.
- Explain why sharing passwords with third-party applications is dangerous.
- Identify the four core OAuth 2.0 roles.
- Explain the relationship between a Client, Resource Owner, Authorization Server, and Resource Server.
- Explain what an Access Token represents.
- Explain what an Authorization Grant is.
- Understand the high-level OAuth 2.0 authorization process.
- Distinguish OAuth 2.0 authorization from OpenID Connect authentication.
- Understand why the Authorization Code flow exists.
- Recognize how OAuth 2.0 fits into the Microsoft Entra ID laboratory.

---

# 2. The Problem OAuth 2.0 Solves

Before understanding OAuth 2.0, we need to understand the problem it addresses.

Imagine that you are using a third-party application that wants to access your data from another service.

For example:

```text
You
 │
 │ Want to use
 ▼
Third-Party Application
 │
 │ Needs access to
 ▼
Your Data on Another Service
```

A naive approach might be:

```text
User
 │
 │ Gives username + password
 ▼
Third-Party Application
 │
 │ Uses credentials
 ▼
Resource Server
```

For example:

```text
User
 │
 │ Gives Microsoft password
 ▼
Third-Party Application
 │
 │ Logs in as the user
 ▼
Microsoft Service
```

This creates several serious problems.

---

## 2.1 The Third Party Receives the User's Password

The application now possesses the user's credentials.

```text
User Password
      │
      ▼
Third-Party Application
```

This means the user must trust the third-party application with one of their most sensitive secrets.

If the application is compromised:

```text
Attacker
    │
    ▼
Third-Party Application
    │
    ▼
Stored User Credentials
```

The user's password may be exposed.

---

## 2.2 Passwords Cannot Easily Express Limited Permission

A password usually represents broad access to an account.

For example:

```text
Password
    │
    ▼
Full Account Access
```

But the user may only want an application to:

```text
Read calendar
```

and not:

```text
Read email
Delete files
Change password
Manage account
```

The user needs a way to delegate **limited access**.

---

## 2.3 Access Should Be Revocable

Suppose the user no longer trusts the application.

The user should be able to do this:

```text
User
 │
 │ Revoke access
 ▼
Third-Party Application
 │
 └── Cannot access resource anymore
```

Without needing to change their account password.

---

## 2.4 OAuth 2.0 Introduces Delegated Authorization

OAuth 2.0 provides a framework that allows a resource owner to grant limited access to protected resources without sharing their credentials with the client.

Conceptually:

```text
Without OAuth

User
 │
 │ Shares password
 ▼
Application
 │
 ▼
Resource Server
```

With OAuth:

```text
With OAuth

User
 │
 │ Authorizes access
 ▼
Authorization Server
 │
 │ Issues token
 ▼
Application
 │
 │ Uses token
 ▼
Resource Server
```

The important change is:

```text
Password
    ≠
Access Token
```

The application does not need the user's password.

Instead, it receives a credential that represents authorized access.

---

# 3. What Is OAuth 2.0?

OAuth 2.0 is an authorization framework.

RFC 6749 defines OAuth 2.0 as a framework that enables a third-party application to obtain limited access to an HTTP service.

A simplified interpretation is:

```text
Resource Owner
      │
      │ Grants permission
      ▼
Client
      │
      │ Receives an access token
      ▼
Resource Server
```

The Access Token allows the Client to access protected resources according to the authorization granted.

The important point is:

> **OAuth 2.0 is designed around delegated authorization.**

OAuth 2.0 answers a question such as:

```text
Can this application access this protected resource
on behalf of this user?
```

For example:

```text
Calendar Application
        │
        │ Can read
        ▼
User's Calendar
```

while:

```text
Calendar Application
        │
        │ Cannot access
        ▼
User's Email
```

depending on the permissions that were granted.

---

# 4. The Four Core Roles

OAuth 2.0 defines four main roles.

```text
┌─────────────────────┐
│   Resource Owner    │
│                     │
│ Usually the User    │
└──────────┬──────────┘
           │
           │ Grants authorization
           ▼
┌─────────────────────┐
│       Client        │
│                     │
│ Application that    │
│ requests access     │
└──────────┬──────────┘
           │
           │ Obtains token from
           ▼
┌─────────────────────┐
│ Authorization Server│
│                     │
│ Issues tokens       │
└─────────────────────┘

           Client
             │
             │ Access Token
             ▼

┌─────────────────────┐
│   Resource Server   │
│                     │
│ Protected API/Data  │
└─────────────────────┘
```

The roles are defined below.

---

# 5. Resource Owner

The **Resource Owner** is the entity capable of granting access to a protected resource.

In many OAuth scenarios, the Resource Owner is a human user.

For example:

```text
Alice
  │
  ▼
Owns access rights to
  │
  ▼
Microsoft Resources
```

Alice can decide:

```text
Allow Application
```

or:

```text
Deny Application
```

The Resource Owner does not necessarily have to be a human, but in the context of our Microsoft Entra ID lab, it will commonly be the user.

---

# 6. Client

The **Client** is the application that requests access to protected resources.

For example:

```text
Your Application
```

The Client might be:

```text
Web Application
Single-Page Application
Mobile Application
Desktop Application
Server Application
```

In our laboratory:

```text
Your Local Application
        │
        │ Requests authorization
        ▼
Microsoft Entra ID
```

The Client is identified to the Authorization Server.

Depending on the application type and security model, the Client may also authenticate to the Authorization Server.

A simplified view is:

```text
Client
 │
 ├── client_id
 │
 └── Other registration / authentication properties
```

We will study application registration later when we register an application with Microsoft Entra ID.

---

# 7. Authorization Server

The **Authorization Server** is responsible for issuing tokens to the Client after the appropriate authorization process.

Conceptually:

```text
Client
   │
   │ Requests authorization
   ▼
Authorization Server
   │
   │ Interacts with Resource Owner
   ▼
Authorization Decision
   │
   │
   ▼
Token
```

The Authorization Server may:

- Authenticate the Resource Owner.
- Obtain authorization from the Resource Owner.
- Validate the Client where applicable.
- Issue authorization artifacts.
- Issue Access Tokens.

In our future laboratory:

```text
Microsoft Entra ID
        │
        ▼
Authorization Server
```

However, remember that a real identity platform can perform multiple roles depending on the protocol and architecture.

---

# 8. Resource Server

The **Resource Server** hosts protected resources.

For example:

```text
Protected API
User Data
Calendar API
File API
Profile API
```

The Client sends an Access Token when requesting access.

```text
Client
   │
   │ Authorization: Bearer <access_token>
   ▼
Resource Server
   │
   │ Validate token / authorization
   ▼
Protected Resource
```

The Resource Server uses the access token according to its authorization and security model to determine whether the request should be allowed.

---

# 9. The OAuth 2.0 Actors Together

We can now connect all four roles.

```text
┌──────────────────┐
│  Resource Owner  │
│                  │
│      User        │
└────────┬─────────┘
         │
         │ Authorizes
         ▼
┌──────────────────┐
│ Authorization    │
│ Server           │
│                  │
│ Microsoft Entra  │
└────────┬─────────┘
         │
         │ Issues Access Token
         ▼
┌──────────────────┐
│      Client      │
│                  │
│ Your Application │
└────────┬─────────┘
         │
         │ Sends Access Token
         ▼
┌──────────────────┐
│ Resource Server  │
│                  │
│ Protected API    │
└──────────────────┘
```

Another way to understand the flow is:

```text
User
 │
 │ "I allow this application to access X."
 ▼
Authorization Server
 │
 │ "Here is a token representing that authorization."
 ▼
Client
 │
 │ "I present this token to access X."
 ▼
Resource Server
```

---

# 10. Protected Resources

OAuth exists because applications often need access to resources protected by another system.

Examples include:

```text
Microsoft Graph
Google Calendar
GitHub API
File Storage API
Internal Company API
```

A resource might conceptually look like:

```text
/api/calendar
/api/profile
/api/files
/api/messages
```

Without valid authorization:

```text
Client
   │
   ▼
Protected Resource
   │
   └── Access Denied
```

With valid authorization:

```text
Client
   │
   │   Access Token
   ▼
Protected Resource
   │
   └── Access Granted
```

---

# 11. What Is an Access Token?

An **Access Token** is a credential used by the Client to access protected resources.

Conceptually:

```text
Access Token
      │
      ▼
Proof of Granted Access
```

The Client might send it using the HTTP `Authorization` header:

```http
GET /api/resource HTTP/1.1
Host: resource.example.com
Authorization: Bearer <access-token>
```

The token is presented to the Resource Server.

```text
Client
   │
   │ Bearer Access Token
   ▼
Resource Server
```

The Resource Server then evaluates the token according to the authorization system.

Important:

> **An Access Token is intended for accessing a protected resource.**

It is not automatically a general-purpose identity document.

Later, when we study OpenID Connect, we will compare:

```text
Access Token
    ↓
Access to Resource
```

with:

```text
ID Token
    ↓
Information about Authentication / Identity
```

---

# 12. Authorization Grant

OAuth 2.0 defines an **Authorization Grant** as a credential representing the Resource Owner's authorization.

The Client can use an Authorization Grant to obtain an Access Token.

Conceptually:

```text
Resource Owner
      │
      │ Authorization
      ▼
Authorization Grant
      │
      │ Presented to
      ▼
Authorization Server
      │
      ▼
Access Token
```

OAuth 2.0 defines several grant types.

Historically, RFC 6749 describes:

```text
Authorization Code
Implicit
Resource Owner Password Credentials
Client Credentials
```

However, not all of these are appropriate for modern applications.

The OAuth 2.0 Security Best Current Practice recommends against using the Implicit grant and the Resource Owner Password Credentials grant.

For this laboratory, our primary focus will be:

```text
Authorization Code
        +
PKCE
```

because it is the modern approach used for many application types.

---

# 13. High-Level OAuth 2.0 Flow

At a high level, the authorization process looks like this:

```text
    ┌──────────────┐
    │     User     │
    └──────┬───────┘
           │
           │ 1. Wants to use application
           ▼
    ┌──────────────┐
    │    Client    │
    │ Application  │
    └──────┬───────┘
           │
           │ 2. Authorization Request
           ▼
┌──────────────────────┐
│ Authorization Server │
└──────────┬───────────┘
           │
           │ 3. User authentication + authorization
           │
           ▼
    ┌──────────────┐
    │     User     │
    └──────────────┘
           │
           │ 4. Authorization Result
           ▼
    ┌──────────────┐
    │    Client    │
    └──────┬───────┘
           │
           │ 5. Obtain Access Token
           ▼
┌──────────────────────┐
│ Authorization Server │
└──────────┬───────────┘
           │
           │ 6. Access Token
           ▼
    ┌──────────────┐
    │    Client    │
    └──────┬───────┘
           │
           │ 7. Access Token
           ▼
┌──────────────────────┐
│   Resource Server    │
└──────────────────────┘
```

The exact details depend on the authorization flow being used.

---

# 14. Why Not Send the User's Password to the Client?

This is the core motivation for OAuth.

Compare these two approaches.

## Without OAuth

```text
User
 │
 │ Username + Password
 ▼
Third-Party Application
 │
 │ Stores / uses credentials
 ▼
Resource Server
```

The application now has access to the user's credentials.

Potential problems include:

```text
Credential Theft
Credential Storage Risk
Excessive Permissions
Password Rotation Problems
Difficult Access Revocation
```

---

## With OAuth

```text
User
 │
 │ Authenticates directly with
 ▼
Authorization Server
 │
 │ Authorization result
 ▼
Client
 │
 │ Receives limited credential
 ▼
Access Token
 │
 ▼
Resource Server
```

The Client receives a token rather than the user's password.

This allows access to be:

```text
Scoped
Limited
Revocable
Time-Limited
```

depending on the authorization server and deployment.

---

# 15. Scope

OAuth defines the concept of **scope** as a way to express the requested access.

Conceptually:

```text
Client requests:

read:profile
read:calendar
```

The authorization system can decide what access is granted.

For example:

```text
Requested:

profile.read
calendar.read
email.read
```

The Resource Owner might grant only:

```text
profile.read
calendar.read
```

Conceptually:

```text
Requested Access
       │
       ▼
Authorization Decision
       │
       ▼
Granted Access
```

The exact syntax and semantics of scopes are defined by the authorization system and resource being protected.

In the Microsoft ecosystem, you will later encounter scopes when requesting delegated permissions for resources such as Microsoft Graph.

---

# 16. Delegated Authorization

One of the most useful ways to understand OAuth is through delegation.

Suppose:

```text
Alice
 │
 │ Owns access rights to
 ▼
Calendar
```

Alice wants an application to read the calendar.

OAuth allows:

```text
Alice
 │
 │ Delegates limited access
 ▼
Application
 │
 │ Access Token
 ▼
Calendar API
```

The application is acting with access granted through an authorization process.

The important distinction is:

```text
Application
    ≠
Alice
```

The application is a separate entity.

OAuth provides a mechanism for the application to receive access without receiving Alice's password.

---

# 17. OAuth 2.0 Is Not the Same as Authentication

This is important enough to repeat.

OAuth 2.0 is primarily an authorization framework.

A successful OAuth authorization flow does not, by itself, define a standard identity layer for telling the Client:

```text
"This is Alice."
```

OpenID Connect extends OAuth 2.0 with standardized identity functionality.

A useful comparison is:

```text
OAuth 2.0

"May this Client access this Resource?"
```

versus:

```text
OpenID Connect

"Who is the authenticated End-User?"
```

In practice, the same identity platform may support both OAuth 2.0 and OpenID Connect.

For example:

```text
Microsoft Entra ID
       │
       ├── OAuth 2.0
       │       │
       │       └── Authorization
       │
       └── OpenID Connect
               │
               └── Authentication + Identity
```

We will study their relationship in more detail in later lectures.

---

# 18. OAuth 2.0 Does Not Mean "Login"

A common simplification is:

```text
"Login with OAuth"
```

This phrase is widely used, but technically it can hide an important distinction.

OAuth 2.0 itself focuses on authorization.

If an application wants standardized information about:

```text
Who authenticated?
```

then OpenID Connect provides an identity layer.

Therefore:

```text
OAuth 2.0
    ≠
Complete standardized authentication protocol by itself
```

while:

```text
OAuth 2.0 + OpenID Connect
    ↓
Authorization + standardized identity layer
```

This distinction is important for our lab because we are investigating how an application can identify a Microsoft user.

That will eventually involve OpenID Connect and ID Tokens.

---

# 19. Introduction to Authorization Code

The **Authorization Code** is one type of Authorization Grant.

Instead of directly returning an Access Token through the browser, the Authorization Server can return a short-lived Authorization Code.

Conceptually:

```text
User
 │
 ▼
Authorization Server
 │
 │ Authorization Code
 ▼
Client
 │
 │ Exchanges code
 ▼
Authorization Server
 │
 │ Access Token
 ▼
Client
```

This is important because the Authorization Code is an intermediate artifact.

It is exchanged at the token endpoint for tokens.

Conceptually:

```text
Authorization Code
        │
        │ Temporary credential
        ▼
Token Endpoint
        │
        ▼
Access Token
```

We will study this in detail in:

```text
docs/02-oauth-flow/02-authorization-code.md
```

For modern OAuth deployments, the Authorization Code flow is commonly combined with PKCE.

---

# 20. Introduction to PKCE

PKCE stands for:

```text
Proof Key for Code Exchange
```

PKCE adds protection to the Authorization Code flow by binding the authorization request to the token exchange through a cryptographic value.

At a high level:

```text
Client
 │
 │ Creates secret verifier
 ▼
code_verifier
 │
 │ Creates derived value
 ▼
code_challenge
 │
 │
 ▼
Authorization Server
```

Later:

```text
Authorization Code
        +
code_verifier
        │
        ▼
Token Endpoint
        │
        ▼
Validate PKCE Binding
```

This helps protect against authorization code interception attacks.

PKCE is defined in RFC 7636.

We will study it in detail in:

```text
docs/06-security/03-pkce.md
```

---

# 21. OAuth 2.0 in Our Microsoft Entra ID Lab

Our lab will eventually use Microsoft Entra ID as an identity and authorization platform.

A simplified architecture will look like:

```text
    ┌──────────────┐
    │     User     │
    └──────┬───────┘
           │
           │ Uses
           ▼
┌─────────────────────┐
│  Your Application   │
│      (Client)       │
└──────────┬──────────┘
           │
           │ Authorization Request
           ▼
┌─────────────────────┐
│ Microsoft Entra ID  │
│ Authorization Server│
└──────────┬──────────┘
           │
           │ Authorization Result
           ▼
┌─────────────────────┐
│  Your Application   │
│      (Client)       │
└──────────┬──────────┘
           │
           │ Access Token
           ▼
┌─────────────────────┐
│ Protected Resource  │
│ / Resource Server   │
└─────────────────────┘
```

Later, when OpenID Connect is added:

```text
Microsoft Entra ID
        │
        ├── Access Token
        │       │
        │       └── Authorization
        │
        └── ID Token
                │
                └── Authentication / Identity
```

One of the goals of this repository is to observe these artifacts directly rather than only reading about them.

---

# 22. Key Takeaways

## OAuth 2.0

```text
OAuth 2.0
    ↓
Authorization Framework
```

## Resource Owner

```text
Resource Owner
    ↓
Entity capable of granting access
```

## Client

```text
Client
    ↓
Application requesting access
```

## Authorization Server

```text
Authorization Server
    ↓
Authorization process
    +
Token issuance
```

## Resource Server

```text
Resource Server
    ↓
Hosts protected resources
```

## Access Token

```text
Access Token
    ↓
Credential used to access protected resources
```

## Authorization Code

```text
Authorization Code
    ↓
Temporary authorization artifact
    ↓
Exchanged for tokens
```

---

# 23. Knowledge Check

Before moving to the next lecture, make sure you can answer these questions.

### Question 1

What problem does OAuth 2.0 primarily solve?

```text
Answer:

OAuth 2.0 provides a framework for delegated authorization,
allowing an application to obtain limited access to protected
resources without requiring the user to share their password
with that application.
```

---

### Question 2

Who is the Resource Owner?

```text
Answer:

The entity capable of granting access to a protected resource.

In many scenarios, this is the user.
```

---

### Question 3

What is the Client?

```text
Answer:

The application that requests access to protected resources.
```

---

### Question 4

What does the Authorization Server do?

```text
Answer:

It participates in the authorization process and issues
tokens to the Client according to the applicable OAuth flow.
```

---

### Question 5

What is the Resource Server?

```text
Answer:

The server that hosts protected resources and accepts
authorized requests using access tokens.
```

---

### Question 6

What is an Access Token primarily used for?

```text
Answer:

To access protected resources.
```

---

### Question 7

Does OAuth 2.0 require the user to give their password to the Client?

```text
Answer:

No.

A primary purpose of OAuth is to allow delegated access
without requiring the user to share their credentials with
the Client.
```

---

### Question 8

Is OAuth 2.0 itself an identity layer that standardizes how a Client learns who the End-User is?

```text
Answer:

No.

OpenID Connect provides a standardized identity layer
on top of OAuth 2.0.
```

---

### Question 9

What is an Authorization Code?

```text
Answer:

An Authorization Grant that can be exchanged at the token
endpoint for tokens in the Authorization Code flow.
```

---

### Question 10

What modern security mechanism is commonly used with the Authorization Code flow?

```text
Answer:

PKCE
(Proof Key for Code Exchange)
```

---

# 24. Preview of the Next Lecture

The next lecture introduces OpenID Connect:

```text
docs/01-foundations/03-openid-connect.md
```

We will answer:

```text
Why is OAuth 2.0 not enough for standardized authentication?

What problem does OpenID Connect solve?

What is an OpenID Provider?

What is a Relying Party?

What is an ID Token?

What are Claims?

How does an application learn who authenticated?
```

This lecture will move us from:

```text
"Can this application access this resource?"
```

toward:

```text
"Who is the authenticated user?"
```

---

# 25. References

This lecture is based primarily on standards and security guidance.

---

## 25.1 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

RFC 6749 defines the OAuth 2.0 authorization framework.

It defines core concepts including:

```text
Resource Owner
Client
Authorization Server
Resource Server
Authorization Grant
Access Token
Scope
Authorization Code
```

Source:

https://www.rfc-editor.org/rfc/rfc6749

---

## 25.2 IETF RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

RFC 7636 defines PKCE.

PKCE provides additional protection for the Authorization Code flow by binding the authorization request and token exchange through a code verifier and code challenge.

Source:

https://www.rfc-editor.org/rfc/rfc7636

---

## 25.3 RFC 9700 — Best Current Practice for OAuth 2.0 Security

RFC 9700 provides current security guidance and best current practices for OAuth 2.0.

It updates and consolidates security recommendations beyond the original OAuth 2.0 specification.

Relevant topics include:

```text
Authorization Code Flow
PKCE
Redirect URI Security
Client Security
Authorization Server Security
Access Token Security
Deprecated / Discouraged Flows
```

Source:

https://www.rfc-editor.org/rfc/rfc9700

---

## 25.4 OpenID Connect Core 1.0

OpenID Connect defines an identity layer built on top of OAuth 2.0.

It is relevant to this lecture because OAuth 2.0 authorization concepts form the foundation on which OpenID Connect adds standardized identity functionality.

Source:

https://openid.net/specs/openid-connect-core-1_0.html

---

# 26. Source Hierarchy Used in This Lecture

The concepts in this lecture should be understood using the following source hierarchy:

```text
                    Standards
                       │
          ┌────────────┴────────────┐
          │                         │
         IETF                    OpenID
          │                     Foundation
          │                         │
      OAuth RFCs                OIDC Specs
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
               Security Guidance
                       │
                       ▼
             Vendor Documentation
                       │
                       ▼
                Blog / Tutorial
```

For this repository:

```text
IETF RFC 6749
    ↓
OAuth 2.0 Core Concepts

IETF RFC 7636
    ↓
PKCE

RFC 9700
    ↓
OAuth 2.0 Security Best Current Practice

OpenID Foundation
    ↓
OpenID Connect Identity Layer

Microsoft Documentation
    ↓
Microsoft Entra ID Implementation
```

The purpose is to distinguish between:

```text
Protocol Definition
```

and:

```text
Provider-Specific Implementation
```

For example:

```text
OAuth 2.0
    ↓
Defined by IETF standards

Microsoft Entra OAuth Endpoints
    ↓
Microsoft implementation of relevant standards
```

---

# 27. Lecture Completion Checklist

Before proceeding, verify that you can explain:

- [ ] What problem OAuth 2.0 solves.
- [ ] Why sharing user passwords with third-party applications is dangerous.
- [ ] Resource Owner.
- [ ] Client.
- [ ] Authorization Server.
- [ ] Resource Server.
- [ ] Protected Resource.
- [ ] Authorization Grant.
- [ ] Access Token.
- [ ] Scope.
- [ ] Delegated Authorization.
- [ ] Authorization Code.
- [ ] PKCE.
- [ ] Why OAuth 2.0 is not the same as OpenID Connect.
- [ ] The difference between an Access Token and an ID Token.

If these concepts are clear, continue to:

```text
docs/01-foundations/03-openid-connect.md
```

The next lecture will introduce the identity layer that allows an application to move from:

```text
"What access has been granted?"
```

to:

```text
"Who authenticated?"
```