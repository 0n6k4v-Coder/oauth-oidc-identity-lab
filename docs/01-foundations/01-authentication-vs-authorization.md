# Lecture 01 — Authentication vs Authorization

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Basic understanding of HTTP, web applications, and client/server architecture

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain what Authentication means.
- Explain what Authorization means.
- Clearly distinguish Authentication from Authorization.
- Explain why Authentication normally happens before Authorization.
- Identify the roles of a User, Client, Resource Server, and Identity Provider.
- Understand where Authentication and Authorization appear in a modern web application.
- Understand why OAuth 2.0 and OpenID Connect are related but solve different problems.
- Connect these concepts to the Microsoft Entra ID lab that follows.

---

# 2. The Fundamental Question

When a user accesses a protected resource, a system usually needs to answer two different questions.

```text
Question 1:

"Who are you?"

        ↓

Authentication
````

and:

```text
Question 2:

"What are you allowed to do?"

        ↓

Authorization
```

These questions are related, but they are **not the same security decision**.

A useful mental model is:

```text
              ┌─────────────────┐
              │      User       │
              └────────┬────────┘
                       │
                       │ Prove identity
                       ▼
              ┌─────────────────┐
              │ Authentication  │
              └────────┬────────┘
                       │
                       │ "Who is this?"
                       ▼
                 Authenticated
                    Identity
                       │
                       │ Evaluate permissions
                       ▼
              ┌─────────────────┐
              │  Authorization  │
              └────────┬────────┘
                       │
                       │ "What can they do?"
                       ▼
              ┌─────────────────┐
              │ Access Decision │
              └─────────────────┘
```

---

# 3. Authentication

## 3.1 Definition

NIST defines authentication as the process of verifying the identity of a user, process, or device, often as a prerequisite to allowing access to resources.

In NIST's current digital identity guidance, authentication is described in terms of a claimant proving possession and control of one or more authenticators bound to a subscriber account.

In simpler terms:

> **Authentication is the process of establishing confidence that an entity is the entity it claims to be.**

Source:

* NIST CSRC Glossary — Authentication
* NIST SP 800-63-4

See the source links in the [References](#20-references) section.

---

## 3.2 The Question Authentication Answers

Authentication answers:

```text
"Who is this?"
```

For example:

```text
User claims:

"I am Alice."
```

The system then requires evidence.

For example:

```text
Username + Password
```

or:

```text
Password + One-Time Password
```

or:

```text
Passkey
```

or:

```text
Hardware Security Key
```

or, in a federated authentication system:

```text
Microsoft Entra ID
        │
        │ Authenticates user
        ▼
Your Application
```

The important distinction is:

```text
Claimed Identity
        +
Evidence
        ↓
Authentication Decision
```

---

# 4. Authentication Factors

Authentication can involve different kinds of authenticators.

A common classification is:

```text
Something you know
        │
        ├── Password
        └── PIN

Something you have
        │
        ├── Security Key
        ├── Hardware Token
        └── Authenticator Device

Something you are
        │
        ├── Fingerprint
        ├── Face
        └── Other Biometrics
```

NIST SP 800-63-4 uses the concept of authenticators and authentication factors when describing digital identity authentication.

The important idea for this laboratory is not memorizing the categories.

The important idea is:

> **Authentication requires evidence that provides confidence in the claimed identity.**

---

# 5. Authorization

## 5.1 Definition

NIST defines authorization as:

> The right or permission granted to a system entity to access a system resource.

Authorization can also be understood as the process of determining whether a requested action or service is approved for a particular entity.

In simpler terms:

> **Authorization determines what an authenticated entity is allowed to access or perform.**

---

## 5.2 The Question Authorization Answers

Authorization answers:

```text
"What is this entity allowed to do?"
```

For example:

```text
Alice
 │
 ├── Read profile       ✓
 ├── Edit profile       ✓
 ├── Delete account     ✓
 └── Manage other users ✗
```

Authentication established:

```text
Alice is Alice.
```

Authorization determines:

```text
Alice can perform X.
Alice cannot perform Y.
```

---

# 6. Authentication vs Authorization

The simplest comparison is:

|               | Authentication                                   | Authorization                                     |
| ------------- | ------------------------------------------------ | ------------------------------------------------- |
| Main question | Who are you?                                     | What can you do?                                  |
| Purpose       | Establish identity                               | Determine access                                  |
| Concern       | Identity                                         | Permissions                                       |
| Happens       | Usually before authorization                     | After or based on an established identity/context |
| Example       | Login with password                              | Allow access to `/admin`                          |
| Result        | Authenticated identity                           | Allow / Deny                                      |
| Typical data  | Credentials, authenticators, identity assertions | Roles, permissions, policies, scopes, attributes  |

A useful shorthand is:

```text
Authentication
    =
Identity

Authorization
    =
Permission
```

But remember that this is a mental model, not a complete formal definition.

---

# 7. A Simple Example

Imagine an application with three users:

```text
Alice
Bob
Charlie
```

The application has an administration page:

```text
/admin
```

The system needs to answer two questions.

### Step 1 — Authentication

Alice signs in.

```text
Alice
 │
 │ Credentials / Authentication
 ▼
Authentication System
 │
 │
 ▼
"Authenticated as Alice"
```

The application now knows which identity is associated with the session.

### Step 2 — Authorization

The application checks Alice's permissions.

```text
Alice
 │
 │ Is Alice an administrator?
 ▼
Authorization Policy
 │
 ├── YES → Allow
 └── NO  → Deny
```

Therefore:

```text
Authentication:
"You're Alice."

Authorization:
"Alice is allowed to access /admin."
```

---

# 8. Authentication Does Not Automatically Mean Authorization

This is one of the most important concepts in this course.

A successful login does **not** necessarily mean that the user can access everything.

For example:

```text
User
 │
 ▼
Authentication
 │
 │ Success
 ▼
Authenticated User
 │
 ├── Public Profile       ✓
 ├── Own Documents        ✓
 ├── Admin Dashboard      ✗
 └── Other User's Data    ✗
```

The user can be completely authenticated while still being denied access to a resource.

This distinction is fundamental to access-control systems.

---

# 9. The HTTP Perspective

HTTP provides mechanisms for communicating authentication information.

For example, RFC 9110 defines the HTTP authentication framework and the `Authorization` request header.

A request might conceptually look like:

```http
GET /api/profile HTTP/1.1
Host: example.com
Authorization: Bearer <access-token>
```

The server can use the supplied credentials to authenticate the request according to the applicable authentication scheme.

However:

```text
Valid Authentication
        ≠
Automatic Permission
```

The application still needs to determine whether the authenticated principal is allowed to perform the requested operation.

RFC 9110 also distinguishes between authentication failure and authorization failure. For example, a server may use:

```text
401 Unauthorized
```

when authentication credentials are missing or invalid, while:

```text
403 Forbidden
```

indicates that the request has been understood but access is not permitted.

See:

* RFC 9110, Section 11 — HTTP Authentication
* RFC 9110, Section 15.5 — HTTP Status Codes

---

# 10. Authentication in a Modern Web Application

A simplified architecture might look like this:

```text
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                           │ Login
                           ▼
                  ┌──────────────────┐
                  │ Identity Provider│
                  │                  │
                  │ Microsoft Entra  │
                  └────────┬─────────┘
                           │
                           │ Authentication Result
                           ▼
                  ┌──────────────────┐
                  │    Web App       │
                  └────────┬─────────┘
                           │
                           │ Authenticated Identity
                           ▼
                  ┌──────────────────┐
                  │ Authorization    │
                  │ Policy           │
                  └────────┬─────────┘
                           │
                    ┌──────┴───────┐
                    │              │
                  Allow           Deny
                    │              │
                    ▼              ▼
                 Resource        403
```

The Identity Provider can perform the authentication.

The application remains responsible for deciding what the authenticated identity is allowed to do within the application's own resources.

---

# 11. Identity Provider

An **Identity Provider (IdP)** is a system that provides identity and authentication services.

Examples include:

```text
Microsoft Entra ID
Google
GitHub
Okta
Auth0
```

In this laboratory, Microsoft Entra ID will be our first real Identity Provider.

The conceptual relationship is:

```text
                 Authentication
                       │
                       ▼
              ┌─────────────────┐
              │ Microsoft Entra │
              │       ID        │
              └────────┬────────┘
                       │
                       │ Identity information
                       ▼
              ┌─────────────────┐
              │   Your Web App  │
              └─────────────────┘
```

The important question for later lectures will be:

> How can our application trust the identity information received from the Identity Provider?

We will answer this through OpenID Connect, ID Tokens, issuers, signatures, JWKS, and token validation.

---

# 12. Where OAuth 2.0 Fits

At this point, it is important not to confuse OAuth 2.0 with authentication.

OAuth 2.0 is an authorization framework.

RFC 6749 describes OAuth 2.0 as a framework that allows a third-party application to obtain limited access to an HTTP service.

A simplified OAuth model is:

```text
Resource Owner
      │
      │ Authorization
      ▼
Authorization Server
      │
      │ Access Token
      ▼
Client
      │
      │ Access Token
      ▼
Resource Server
```

The important concept is:

```text
OAuth 2.0
    ↓
Delegated Authorization
    ↓
Access to Resources
```

OAuth 2.0 itself does not define a standard identity layer for telling a client who the End-User is.

That is where OpenID Connect enters.

---

# 13. Where OpenID Connect Fits

OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0.

The OpenID Foundation defines OpenID Connect as a simple identity layer on top of OAuth 2.0 that allows a Client to verify the identity of the End-User based on authentication performed by an Authorization Server.

Conceptually:

```text
OAuth 2.0
    │
    │ Authorization framework
    ▼
Access to Resources
```

while:

```text
OpenID Connect
    │
    │ Identity layer
    ▼
Authentication + Identity Information
```

OpenID Connect introduces the:

```text
ID Token
```

which is a JWT containing claims about the authentication event and, potentially, the End-User.

---

# 14. OAuth 2.0 vs OpenID Connect

|                         | OAuth 2.0                        | OpenID Connect            |
| ----------------------- | -------------------------------- | ------------------------- |
| Primary purpose         | Authorization                    | Authentication / Identity |
| Main question           | What may the client access?      | Who authenticated?        |
| Token commonly involved | Access Token                     | ID Token                  |
| Built on                | OAuth framework                  | OAuth 2.0                 |
| Identity information    | Not standardized by OAuth itself | Standardized through OIDC |
| Used in this lab        | Yes                              | Yes                       |

A useful mental model:

```text
OAuth 2.0
    │
    └── Authorization

OpenID Connect
    │
    └── Identity / Authentication
          │
          └── Built on OAuth 2.0
```

---

# 15. Authentication, Authorization, and Identity

These concepts should be kept separate.

```text
Identity
   │
   │ "Who is this entity?"
   ▼
Authentication
   │
   │ "Can we establish confidence in that identity?"
   ▼
Authenticated Identity
   │
   │ "What is this identity allowed to do?"
   ▼
Authorization
   │
   ▼
Access Decision
```

This distinction becomes especially important when designing a database.

For example, our application may eventually contain:

```text
users
```

for its internal users, while:

```text
user_identities
```

maps those users to identities from external Identity Providers.

Conceptually:

```text
Microsoft Entra Identity
          │
          │ Authentication
          ▼
   External Identity
          │
          │ Mapping
          ▼
       user_id
          │
          ▼
   Application User
          │
          │ Authorization
          ▼
     Permissions
```

We will design this in a later lecture.

---

# 16. Why This Distinction Matters for Our Lab

Our laboratory is going to investigate a real Microsoft Entra authentication flow.

Eventually we will observe something similar to:

```text
User
 │
 │ 1. Login
 ▼
Microsoft Entra ID
 │
 │ 2. Authentication
 ▼
Microsoft Entra ID
 │
 │ 3. Authorization Code
 ▼
Our Application
 │
 │ 4. Token Exchange
 ▼
Microsoft Entra ID
 │
 │ 5. ID Token
 ▼
Our Application
 │
 │ 6. Validate Identity
 ▼
Authenticated Identity
 │
 │ 7. Application Authorization
 ▼
Access Decision
```

This gives us two separate trust decisions:

### Identity Provider's decision

```text
"Who authenticated?"
```

### Application's decision

```text
"What is this identity allowed to do in my application?"
```

Keeping these decisions separate is one of the foundations of a maintainable identity architecture.

---

# 17. Key Takeaways

## Authentication

```text
Authentication
    ↓
Verify / establish confidence in identity
    ↓
"Who are you?"
```

## Authorization

```text
Authorization
    ↓
Determine permitted access or actions
    ↓
"What are you allowed to do?"
```

## OAuth 2.0

```text
OAuth 2.0
    ↓
Authorization framework
    ↓
Delegated access to resources
```

## OpenID Connect

```text
OpenID Connect
    ↓
Identity layer on OAuth 2.0
    ↓
Authentication + identity claims
```

---

# 18. Knowledge Check

Before moving to the next lecture, make sure you can answer these questions without looking at the notes.

### Question 1

A user enters a password.

What security concept is primarily involved?

```text
Answer:
Authentication
```

### Question 2

A system checks whether a user can delete another user's account.

What security concept is primarily involved?

```text
Answer:
Authorization
```

### Question 3

Can a user be authenticated but not authorized to access a resource?

```text
Answer:
Yes.
```

### Question 4

Does OAuth 2.0 itself define a standard mechanism for communicating the End-User's identity?

```text
Answer:
No.
```

OAuth 2.0 is an authorization framework. OpenID Connect adds an identity layer.

### Question 5

What protocol will we use to study authentication with Microsoft Entra ID?

```text
Answer:
OpenID Connect
```

### Question 6

What token will we investigate later as part of OpenID Connect?

```text
Answer:
ID Token
```

---

# 19. Preview of the Next Lecture

The next lecture introduces OAuth 2.0:

```text
docs/01-foundations/02-oauth-2-overview.md
```

We will answer:

```text
What is OAuth 2.0?

Who are the actors?

What is an Authorization Server?

What is a Resource Server?

What is a Client?

What is an Access Token?

What is an Authorization Code?

Why does the Authorization Code exist?

Why doesn't the application simply receive the Access Token immediately?
```

The concepts from this lecture will become the foundation for understanding the real Microsoft Entra login flow.

---

# 20. References

This lecture intentionally relies on standards and authoritative technical sources rather than vendor-specific tutorials.

## 20.1 NIST — Authentication

**NIST CSRC Glossary — Authentication**

Defines authentication as the process of verifying the identity of a user, process, or device, often as a prerequisite to accessing system resources.

Source:

[https://csrc.nist.gov/glossary/term/authentication](https://csrc.nist.gov/glossary/term/authentication)

---

## 20.2 NIST — Authorization

**NIST CSRC Glossary — Authorization**

Defines authorization in terms of rights or permissions granted to a system entity to access system resources.

Source:

[https://csrc.nist.gov/glossary/term/authorization](https://csrc.nist.gov/glossary/term/authorization)

---

## 20.3 NIST SP 800-63-4 — Digital Identity Guidelines

NIST Special Publication 800-63-4 provides the current Digital Identity Guidelines and defines concepts surrounding authentication, authenticators, identity, and assurance.

Source:

[https://pages.nist.gov/800-63-4/](https://pages.nist.gov/800-63-4/)

---

## 20.4 IETF RFC 9110 — HTTP Semantics

RFC 9110 defines HTTP semantics, including the HTTP authentication framework, authentication challenges, credentials, the `Authorization` header, and relevant HTTP status codes.

Source:

[https://www.rfc-editor.org/rfc/rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html)

Relevant sections:

```text
Section 11  — HTTP Authentication
Section 11.3 — Challenge and Response
Section 11.4 — Credentials
Section 11.6 — Authenticating Users to Origin Servers
Section 15.5 — Client Error 4xx
```

---

## 20.5 IETF RFC 6749 — OAuth 2.0 Authorization Framework

RFC 6749 defines the OAuth 2.0 authorization framework and its roles, authorization grants, access tokens, authorization server, client, and resource server.

Source:

[https://www.rfc-editor.org/rfc/rfc6749.html](https://www.rfc-editor.org/rfc/rfc6749.html)

---

## 20.6 OpenID Foundation — OpenID Connect Core 1.0

OpenID Connect Core 1.0 defines OpenID Connect as an identity layer on top of OAuth 2.0.

It defines concepts including:

```text
OpenID Provider
Relying Party
Authentication
ID Token
Claims
Issuer
Subject
Authorization Code Flow
```

Source:

[https://openid.net/specs/openid-connect-core-1_0.html](https://openid.net/specs/openid-connect-core-1_0.html)

---

# 21. Source Hierarchy Used in This Lecture

When studying this laboratory, prefer sources in approximately this order:

```text
                   Standards
                       │
          ┌────────────┴────────────┐
          │                         │
         IETF                    OpenID
          │                     Foundation
          │                         │
         RFCs                   OIDC Specs
          │                         │
          └────────────┬────────────┘
                       │
                      NIST
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

The purpose is not to avoid tutorials.

Rather:

> **Use standards to establish what a protocol means, and use vendor documentation to understand how a specific provider implements it.**

For this laboratory:

```text
IETF
  ↓
OAuth 2.0

OpenID Foundation
  ↓
OpenID Connect

NIST
  ↓
Identity / Authentication terminology and security guidance

Microsoft
  ↓
Microsoft Entra implementation
```

This distinction will become increasingly important as the lab moves from generic identity concepts into Microsoft Entra ID.

---

# 22. Lecture Completion Checklist

Before proceeding, verify that you can explain all of the following:

* [ ] Authentication
* [ ] Authorization
* [ ] Identity
* [ ] Authenticator
* [ ] Identity Provider
* [ ] Authentication vs Authorization
* [ ] OAuth 2.0
* [ ] OpenID Connect
* [ ] Access Token
* [ ] ID Token
* [ ] Authorization Code
* [ ] Client
* [ ] Authorization Server
* [ ] Resource Server

If these concepts are clear, continue to:

```text
docs/01-foundations/02-oauth-2-overview.md
```

The next lecture will move from **"Who are you?" and "What can you do?"** into the protocol architecture that allows different systems to answer these questions securely.