# Lecture 03 — OpenID Connect

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Authentication vs Authorization and OAuth 2.0 fundamentals

---

# 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain why OAuth 2.0 alone does not standardize End-User identity.
- Explain what OpenID Connect (OIDC) adds on top of OAuth 2.0.
- Identify the roles of an OpenID Provider and Relying Party.
- Explain the purpose of the `openid` scope.
- Understand the purpose of an ID Token.
- Identify important ID Token claims.
- Distinguish an ID Token from an Access Token.
- Explain why token validation is required.
- Connect these concepts to Microsoft Entra ID.

---

# 2. The Problem OAuth 2.0 Does Not Fully Solve

OAuth 2.0 is an authorization framework. It provides a standardized way for a client to obtain limited access to protected resources.

```text
OAuth 2.0
    │
    ▼
Authorization

"What is this client allowed to access?"
```

For example:

```text
User
 │
 │ Authorizes access
 ▼
Application
 │
 │ Receives Access Token
 ▼
Protected API
```

However, OAuth 2.0 by itself does not define a standard identity layer that tells the client:

```text
"Who is the authenticated End-User?"
```

That is the problem OpenID Connect solves.

---

# 3. What Is OpenID Connect?

OpenID Connect, commonly called OIDC, is an identity layer built on top of OAuth 2.0.

It allows a client to verify the identity of an End-User based on authentication performed by an Authorization Server.

Conceptually:

```text
OAuth 2.0
    │
    ▼
Delegated Authorization
```

OpenID Connect adds:

```text
OpenID Connect
    │
    ├── Authentication
    ├── Identity information
    └── Standardized identity protocol
```

A useful mental model is:

```text
OAuth 2.0
=
"What can the application access?"

OpenID Connect
=
"Who authenticated?"
```

---

# 4. OAuth Client and OpenID Connect Relying Party

In OAuth 2.0, your application is called a:

```text
Client
```

In OpenID Connect, the application is also called a:

```text
Relying Party (RP)
```

The application relies on an identity assertion produced by another trusted system.

```text
┌──────────────────┐
│ Your Application │
│                  │
│ Client + RP      │
└────────┬─────────┘
         │
         │ Relies on authentication result
         ▼
┌──────────────────┐
│ OpenID Provider  │
│                  │
│ Microsoft Entra  │
└──────────────────┘
```

The same application can therefore be both an OAuth Client and an OpenID Connect Relying Party.

---

# 5. OpenID Provider

An OAuth Authorization Server that supports OpenID Connect is called an:

```text
OpenID Provider (OP)
```

The OP can:

```text
1. Authenticate the End-User
2. Issue an ID Token
3. Provide identity claims
```

Conceptually:

```text
User
 │
 │ Authenticate
 ▼
OpenID Provider
 │
 │ ID Token
 ▼
Relying Party
```

In this laboratory, Microsoft Entra ID will act as the OpenID Provider.

---

# 6. The `openid` Scope

An OpenID Connect request includes the `openid` scope.

For example:

```text
GET /authorize?
    client_id=...
    &response_type=code
    &redirect_uri=...
    &scope=openid
```

Conceptually:

```text
scope=openid
        │
        ▼
Request OpenID Connect functionality
```

Additional standard scopes can request additional claims:

```text
profile
email
address
phone
```

For example:

```text
scope=openid profile email
```

The important point is that requesting a scope does not allow a client to invent claims or permissions. The OpenID Provider controls what can actually be issued.

---

# 7. The ID Token

The central identity artifact introduced by OpenID Connect is the:

```text
ID Token
```

An ID Token contains claims about the authentication of an End-User and potentially additional information about that user.

An ID Token is represented as a JSON Web Token (JWT).

A simplified example:

```json
{
  "iss": "https://issuer.example.com",
  "sub": "user-123",
  "aud": "my-client-id",
  "exp": 1893456000,
  "iat": 1893452400
}
```

Real tokens can contain additional claims.

---

# 8. Important ID Token Claims

## 8.1 `iss` — Issuer

```text
iss
=
Who issued this token?
```

The Relying Party must verify that the issuer matches an expected trusted issuer.

---

## 8.2 `sub` — Subject

```text
sub
=
Who is the End-User within this issuer's namespace?
```

A subject identifier should be interpreted in the context of its issuer.

Conceptually:

```text
Identity
=
issuer + subject
```

For example, the same `sub` value from two different issuers does not necessarily represent the same person.

---

## 8.3 `aud` — Audience

```text
aud
=
For which client was this ID Token issued?
```

A Relying Party should verify that the token is intended for itself.

---

## 8.4 `exp` — Expiration Time

```text
exp
=
When does this token expire?
```

An expired token must not be accepted as valid.

---

## 8.5 `iat` — Issued At

```text
iat
=
When was this token issued?
```

`iat` and `exp` serve different purposes:

```text
iat = issuance time
exp = expiration time
```

---

# 9. ID Token vs Access Token

| | ID Token | Access Token |
|---|---|---|
| Primary purpose | Authentication and identity claims | Access protected resources |
| Intended consumer | Client / Relying Party | Resource Server |
| Main question | Who authenticated? | What access was granted? |
| Defined by | OpenID Connect | OAuth 2.0 framework |
| JWT required? | OIDC ID Token is a JWT | No fixed format is required by OAuth 2.0 |

A useful model:

```text
ID Token
    │
    ▼
Client / Relying Party

"Here is information about the authenticated user."
```

```text
Access Token
    │
    ▼
Resource Server

"Evaluate this request according to granted authorization."
```

Therefore, tokens must be used according to their intended audience and purpose.

---

# 10. A Simplified OpenID Connect Authorization Code Flow

```text
┌────────┐
│  User  │
└───┬────┘
    │
    │ 1. Click Login
    ▼
┌──────────────────┐
│ Your Application │
│ Client / RP      │
└────────┬─────────┘
         │
         │ 2. Authorization Request
         │    scope=openid
         ▼
┌──────────────────┐
│ OpenID Provider  │
└────────┬─────────┘
         │
         │ 3. Authenticate User
         ▼
      User
         │
         │ 4. Authorization Code
         ▼
┌──────────────────┐
│ Your Application │
└────────┬─────────┘
         │
         │ 5. Exchange Code
         ▼
┌──────────────────┐
│ OpenID Provider  │
└────────┬─────────┘
         │
         │ 6. Token Response
         ├── ID Token
         └── Access Token
```

Receiving an ID Token does not automatically make it trustworthy. The application must validate it.

---

# 11. ID Token Validation

Conceptually:

```text
Receive ID Token
        │
        ▼
Validate Signature
        │
        ▼
Validate Issuer
        │
        ▼
Validate Audience
        │
        ▼
Validate Expiration
        │
        ▼
Validate other required claims
        │
        ▼
Trusted authentication result
```

The exact validation requirements depend on the flow and protocol requirements, but the fundamental principle is:

```text
Token received
≠
Token automatically trusted
```

---

# 12. Why Digital Signatures Matter

Anyone can construct JSON containing claims such as:

```json
{
  "sub": "administrator"
}
```

The claim becomes trustworthy only when the Relying Party can verify that the token was issued by the expected provider and has not been modified.

Conceptually:

```text
Trusted Issuer
      │
      │ Signs token
      ▼
ID Token
      │
      │ Cryptographic validation
      ▼
Trusted identity assertion
```

If a signed payload is modified, signature validation should fail.

Later lectures will explore:

```text
JWT
Digital Signatures
JWKS
Public Keys
Key Rotation
```

---

# 13. UserInfo Endpoint

OpenID Connect can expose a UserInfo Endpoint that returns claims about the authenticated End-User.

Conceptually:

```text
Client
   │
   │ Access Token
   ▼
UserInfo Endpoint
   │
   ▼
Identity Claims
```

A conceptual request:

```http
GET /userinfo HTTP/1.1
Authorization: Bearer <access-token>
```

Possible claims include:

```json
{
  "sub": "user-123",
  "name": "Example User",
  "email": "user@example.com"
}
```

The claims available depend on scopes, provider configuration, consent, and available information.

---

# 14. Mapping an External Identity to an Application User

After validating an ID Token, an application can identify an external identity using the provider context and subject.

Conceptually:

```text
OpenID Provider
       │
       │ issuer + subject
       ▼
External Identity
       │
       │ Mapping
       ▼
Application User
```

A future database model might conceptually contain:

```text
users
```

and:

```text
user_identities
```

For example:

```text
user_identities
────────────────────────
user_id
issuer
subject
provider
created_at
```

The application can use this mapping to connect a trusted external identity to its own internal user and authorization model.

---

# 15. Authentication Is Still Not Authorization

OpenID Connect can establish who authenticated.

Your application must still decide what that user is allowed to do.

```text
OpenID Connect
       │
       ▼
Authenticated Identity
       │
       ▼
Application Authorization
       │
       ├── Roles
       ├── Permissions
       ├── Policies
       └── Resource ownership
```

For example, an authenticated user is not automatically allowed to access:

```text
/admin
```

Your application must make that authorization decision.

---

# 16. Connecting This to Microsoft Entra ID

In our lab, Microsoft Entra ID will conceptually act as both:

```text
OAuth 2.0 Authorization Server
```

and:

```text
OpenID Connect Provider
```

Our application will conceptually be both:

```text
OAuth Client
```

and:

```text
OpenID Connect Relying Party
```

The flow we will investigate is:

```text
User
 │
 ▼
Microsoft Entra ID
 │
 │ Authentication
 ▼
Authorization Code
 │
 ▼
Our Application
 │
 │ Token Exchange
 ▼
ID Token
 │
 │ Validate
 ▼
Trusted External Identity
 │
 ▼
Map to Internal User
 │
 ▼
Application Authorization
```

---

# 17. Key Takeaways

```text
OpenID Connect
=
Identity layer built on OAuth 2.0
```

```text
scope=openid
=
Request OpenID Connect functionality
```

```text
ID Token
=
Authentication and identity claims for the Client / RP
```

Important claims:

```text
iss = Who issued the token?
sub = Who is the subject?
aud = Which client is the token intended for?
exp = When does the token expire?
```

A useful identity model is:

```text
issuer + subject
```

And most importantly:

```text
Received Token
≠
Trusted Token
```

Validation is required.

---

# 18. Knowledge Check

## Question 1

What does OpenID Connect add on top of OAuth 2.0?

```text
Answer:
A standardized identity and authentication layer.
```

## Question 2

What indicates that an authorization request is requesting OpenID Connect functionality?

```text
Answer:
The `openid` scope.
```

## Question 3

What is the primary purpose of an ID Token?

```text
Answer:
To communicate claims about authentication and the authenticated End-User to the Client / Relying Party.
```

## Question 4

What is the difference between an ID Token and an Access Token?

```text
Answer:
An ID Token is intended for the Client / Relying Party and communicates authentication and identity claims.

An Access Token is intended for a Resource Server and is used to authorize access to protected resources.
```

## Question 5

Why should `sub` be interpreted together with the issuer?

```text
Answer:
Different issuers have separate namespaces and can potentially use the same subject value.
```

## Question 6

Can an application trust an ID Token without validation?

```text
Answer:
No. It must validate the token according to the protocol requirements and the application's expected trust configuration.
```

---

# 19. Preview of the Next Lecture

The next lecture is:

```text
docs/01-foundations/04-identity-providers.md
```

We will examine:

```text
What is an Identity Provider?

What is the difference between an IdP, Authorization Server, and OpenID Provider?

How does an application establish trust with an external identity provider?

What information does the application configure before login can happen?
```

---

# 20. References

This lecture uses protocol specifications and standards as its primary sources.

## 20.1 OpenID Foundation — OpenID Connect Core 1.0

The primary specification for OpenID Connect.

It defines concepts including:

```text
OpenID Connect
OpenID Provider
Relying Party
ID Token
Claims
Authentication flows
ID Token validation
UserInfo
```

Source:

<https://openid.net/specs/openid-connect-core-1_0.html>

Relevant sections:

```text
Section 1 — Introduction
Section 2 — ID Token
Section 3 — Authentication
Section 5 — Claims
Section 5.3 — UserInfo Endpoint
Section 3.1.3.7 — ID Token Validation
```

---

## 20.2 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

Defines the OAuth 2.0 framework and concepts including:

```text
Resource Owner
Client
Authorization Server
Resource Server
Authorization Grant
Access Token
```

Source:

<https://www.rfc-editor.org/rfc/rfc6749>

---

## 20.3 IETF RFC 7519 — JSON Web Token (JWT)

Defines JWT, a compact claims representation used by OpenID Connect for ID Tokens.

Source:

<https://www.rfc-editor.org/rfc/rfc7519>

---

## 20.4 OpenID Foundation — OpenID Connect Specifications

The OpenID Foundation maintains the OpenID Connect specification family.

Source:

<https://openid.net/developers/specs/>

---

# 21. Source Hierarchy Used in This Lecture

```text
                    Protocol Standards
                           │
              ┌────────────┴────────────┐
              │                         │
             IETF                  OpenID Foundation
              │                         │
              ▼                         ▼
         OAuth / JWT                  OIDC Specs
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                 Vendor Documentation
                           │
                           ▼
                  Tutorials / Articles
```

The principle is:

> **Use protocol standards to understand what OAuth 2.0 and OpenID Connect define. Use provider documentation to understand how a specific provider implements those standards.**

For this laboratory:

```text
IETF
  │
  └── OAuth 2.0 and JWT

OpenID Foundation
  │
  └── OpenID Connect

Microsoft
  │
  └── Microsoft Entra ID implementation
```

---

# 22. Lecture Completion Checklist

Before proceeding, verify that you can explain:

- [ ] Why OAuth 2.0 alone does not standardize End-User identity.
- [ ] What OpenID Connect adds to OAuth 2.0.
- [ ] What `scope=openid` means.
- [ ] What an OpenID Provider is.
- [ ] What a Relying Party is.
- [ ] What an ID Token is.
- [ ] The difference between an ID Token and an Access Token.
- [ ] The meaning of `iss`.
- [ ] The meaning of `sub`.
- [ ] The meaning of `aud`.
- [ ] The meaning of `exp`.
- [ ] Why an ID Token must be validated.
- [ ] Why `issuer + subject` is an important identity concept.
- [ ] How Microsoft Entra ID fits into the OpenID Connect architecture.

If these concepts are clear, continue to:

```text
docs/01-foundations/04-identity-providers.md
```
