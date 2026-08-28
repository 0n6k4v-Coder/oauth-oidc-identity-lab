# Lecture 04 — Identity Providers

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Level:** Foundation  
> **Prerequisite:** Authentication vs Authorization, OAuth 2.0 Overview, and OpenID Connect

---

# 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain what an Identity Provider (IdP) is.
- Distinguish between an Identity Provider, Authorization Server, and OpenID Provider.
- Understand how an application establishes trust with an external identity provider.
- Explain what information is configured before authentication begins.
- Understand OpenID Connect Discovery.
- Identify the purpose of the OpenID Configuration Document.
- Understand the relationship between `issuer`, `jwks_uri`, and signing keys.
- Explain why an application should not trust arbitrary identity providers or arbitrary public keys.
- Connect these concepts to Microsoft Entra ID.

---

# 2. The Problem We Need to Solve

Imagine that your application receives this ID Token:

```text
ID Token
    │
    ▼

{
  "iss": "https://login.microsoftonline.com/...",
  "sub": "user-123",
  "aud": "your-client-id"
}
```

Your application now has an important question:

```text
"Who gave me this token?"
```

Another question immediately follows:

```text
"Can I trust that issuer?"
```

And then:

```text
"How do I get the real public key
that can verify this token?"
```

These questions introduce the concept of an:

```text
Identity Provider
```

---

# 3. What Is an Identity Provider?

An **Identity Provider**, commonly abbreviated as **IdP**, is a system responsible for providing identity-related services.

Conceptually:

```text
User
 │
 │ Authenticate
 ▼
┌──────────────────────┐
│ Identity Provider    │
│                      │
│  - Authenticate user │
│  - Manage identity   │
│  - Produce assertions│
└──────────┬───────────┘
           │
           │ Identity information
           ▼
┌──────────────────────┐
│ Your Application     │
└──────────────────────┘
```

Examples include Microsoft Entra ID, Google, GitHub, Okta, and Auth0.

An application can delegate the authentication process to an external identity provider.

Instead of:

```text
User
 │
 │ Username + Password
 ▼
Your Application
 │
 ▼
Your Database
```

The architecture can become:

```text
User
 │
 │ Login
 ▼
Identity Provider
 │
 │ Authentication Result
 ▼
Your Application
```

Your application does not necessarily need to handle the user's password directly.

---

# 4. Identity Provider Is a General Concept

An Identity Provider is a general architectural concept.

Different protocols can implement identity services in different ways.

For example:

```text
Identity Provider
       │
       ├── SAML
       │
       ├── OAuth 2.0 + OpenID Connect
       │
       └── Other identity protocols
```

Therefore:

```text
Identity Provider
≠
A specific protocol
```

Instead:

```text
Identity Provider
=
A system that provides identity services
```

---

# 5. Identity Provider vs Authorization Server

These concepts can overlap, but they are not automatically identical.

## Authorization Server

In OAuth 2.0:

```text
Authorization Server
        │
        ├── Authenticates Resource Owner
        ├── Obtains authorization
        └── Issues Access Token
```

OAuth 2.0 defines an Authorization Server as the server that issues access tokens to the client after authenticating the resource owner and obtaining authorization.

The main purpose is:

```text
Authorization
```

## Identity Provider

An Identity Provider focuses on:

```text
Identity
        │
        ├── Who is the user?
        ├── Can the user authenticate?
        └── What identity information can be asserted?
```

---

# 6. OpenID Provider

When an Authorization Server supports OpenID Connect, it becomes an:

```text
OpenID Provider

OP
```

The relationship is:

```text
OAuth 2.0

Authorization Server
        │
        │ + OpenID Connect
        ▼
OpenID Provider
```

An OpenID Provider can:

```text
1. Authenticate the End-User
2. Issue an ID Token
3. Provide identity claims
4. Publish OpenID Connect metadata
5. Publish signing key information
```

Conceptually:

```text
┌──────────────────────┐
│ OpenID Provider      │
│                      │
│ Authentication       │
│ Authorization        │
│ Identity Assertions  │
│ Signing Keys         │
└──────────┬───────────┘
           │
           ▼
      Your Application
```

---

# 7. Microsoft Entra ID in Our Lab

In this laboratory, Microsoft Entra ID plays multiple roles.

Conceptually:

```text
Microsoft Entra ID
        │
        ├── Identity Provider
        │
        ├── OAuth Authorization Server
        │
        └── OpenID Provider
```

Our application also has multiple roles:

```text
Our Application
        │
        ├── OAuth Client
        │
        └── OpenID Connect Relying Party
```

The relationship looks like:

```text
┌──────────────────────┐
│      User            │
└──────────┬───────────┘
           │
           │ Authenticate
           ▼
┌──────────────────────┐
│ Microsoft Entra ID   │
│                      │
│ IdP                  │
│ Authorization Server │
│ OpenID Provider      │
└──────────┬───────────┘
           │
           │ Tokens
           ▼
┌──────────────────────┐
│ Our Application      │
│                      │
│ OAuth Client         │
│ Relying Party        │
└──────────────────────┘
```

---

# 8. The Trust Problem

Suppose an attacker sends your application a JWT.

The token says:

```json
{
  "iss": "Microsoft Entra ID",
  "sub": "administrator",
  "aud": "your-client-id"
}
```

Can your application trust it?

```text
No.
```

Anyone can create JSON containing:

```text
iss
sub
aud
role
email
name
```

Therefore:

```text
Claims alone
≠
Trust
```

The application needs an established trust relationship.

---

# 9. Trust Starts Before the Token Arrives

This is one of the most important concepts in this entire laboratory.

Trust does not begin when the application receives a JWT.

Instead:

```text
Application Configuration
        │
        ▼
Trusted Identity Provider
        │
        ▼
Trusted Metadata Location
        │
        ▼
Trusted Signing Key Source
        │
        ▼
Token Validation
```

Conceptually:

```text
Before Login

Your Application

"I trust Microsoft Entra ID."

        │
        ▼

Expected Issuer

https://login.microsoftonline.com/{tenant-id}/v2.0
```

The application now has a known starting point.

---

# 10. What Does an Application Configure?

Before authentication can begin, the application usually has configuration information such as:

```text
Client ID
Client Secret
Redirect URI
Authority / Issuer
Tenant
Scopes
```

Conceptually:

```text
Application Configuration

CLIENT_ID
CLIENT_SECRET
REDIRECT_URI
AUTHORITY
SCOPES
```

For example:

```text
CLIENT_ID
=
Which application is requesting authentication?
```

```text
REDIRECT_URI
=
Where should the provider send the user back?
```

```text
AUTHORITY
=
Which identity system does this application trust?
```

The authority or issuer configuration becomes the starting point of the trust relationship.

---

# 11. OpenID Connect Discovery

Instead of manually configuring every endpoint, OpenID Connect provides a standardized discovery mechanism.

Conceptually:

```text
Your Application
        │
        │ "Tell me how this OpenID Provider works."
        ▼
OpenID Configuration Document
```

A typical discovery path is:

```text
/.well-known/openid-configuration
```

For Microsoft Entra ID, conceptually:

```text
https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration
```

The metadata document provides endpoint URLs, supported capabilities, and signing-key metadata.

---

# 12. The OpenID Configuration Document

The discovery document is JSON metadata.

A simplified example:

```json
{
  "issuer": "https://login.microsoftonline.com/{tenant-id}/v2.0",

  "authorization_endpoint":
    "https://login.microsoftonline.com/.../authorize",

  "token_endpoint":
    "https://login.microsoftonline.com/.../token",

  "jwks_uri":
    "https://login.microsoftonline.com/.../keys"
}
```

Conceptually:

```text
OpenID Configuration

        │
        ├── Who am I?
        │       │
        │       └── issuer
        │
        ├── Where do users authenticate?
        │       │
        │       └── authorization_endpoint
        │
        ├── Where do I exchange codes?
        │       │
        │       └── token_endpoint
        │
        └── Where are my public keys?
                │
                └── jwks_uri
```

---

# 13. How the Application Finds the Official Public Keys

The flow is:

```text
Step 1

Application is configured
to trust an Identity Provider

        │
        ▼

Step 2

Application accesses the
OpenID Configuration Document

        │
        ▼

Step 3

Application reads:

jwks_uri

        │
        ▼

Step 4

Application requests
the JWKS

        │
        ▼

Step 5

Provider returns
public signing keys
```

Conceptually:

```text
┌──────────────────────┐
│ Your Application     │
└──────────┬───────────┘
           │
           │ Trusted authority
           ▼
┌──────────────────────┐
│ OpenID Discovery     │
│                      │
│ issuer               │
│ authorization...     │
│ token_endpoint       │
│ jwks_uri             │
└──────────┬───────────┘
           │
           │ Follow jwks_uri
           ▼
┌──────────────────────┐
│ JWKS                 │
│                      │
│ Public Key 1         │
│ Public Key 2         │
│ Public Key 3         │
└──────────────────────┘
```

---

# 14. What Is JWKS?

JWKS stands for:

```text
JSON Web Key Set
```

A JWKS contains one or more public keys.

A simplified example:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "kid": "key-123",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

Important fields include:

```text
kty
│
└── Key Type

use
│
└── Intended usage

kid
│
└── Key ID

n
│
└── RSA modulus

e
│
└── RSA exponent
```

---

# 15. How Does the System Choose the Correct Key?

A JWT normally contains a header.

For example:

```json
{
  "alg": "RS256",
  "kid": "key-123"
}
```

The `kid` means:

```text
Key ID
```

The application performs:

```text
JWT
 │
 │ Read header
 ▼

kid = "key-123"

 │
 ▼

Trusted JWKS
 │
 │ Find matching key
 ▼

kid = "key-123"

 │
 ▼

Use matching public key
 │
 ▼

Verify signature
```

The important security rule is:

```text
The JWT can tell you:

"Look for key ID key-123"

But the JWT should NOT tell you:

"Download my key from this attacker-controlled URL"
```

Instead:

```text
JWT
 │
 │ kid = key-123
 ▼

Application

"Let me search for key-123
inside the JWKS of the provider
I already trust."
```

---

# 16. The Complete Trust Chain

We can now see the complete chain.

```text
Application Configuration
        │
        │ Trusted Authority
        ▼
Microsoft Entra ID
        │
        │ OpenID Discovery
        ▼
OpenID Configuration
        │
        │ jwks_uri
        ▼
Microsoft JWKS
        │
        │ Public Keys
        ▼
JWT arrives
        │
        │ kid
        ▼
Find Matching Key
        │
        ▼
Verify Signature
        │
        ▼
Validate Claims
        │
        ├── iss
        ├── aud
        ├── exp
        └── Other required claims
        │
        ▼
Trusted Authentication Result
```

The critical concept is:

```text
Trust does not start here:

JWT
 │
 ▼
"Please trust me."
```

Trust starts here:

```text
Application Configuration
        │
        ▼
Trusted Provider
```

---

# 17. Why Can't an Attacker Simply Publish a Fake Key?

An attacker can create:

```text
Attacker Key Pair

Private Key A
Public Key A
```

They can sign a JWT:

```text
Fake JWT
        │
        ▼
Signed with Private Key A
```

They can even publish a fake JWKS.

But your application should not trust that location.

Your application follows:

```text
Configured Trusted Provider
        │
        ▼
Official Discovery Document
        │
        ▼
Official jwks_uri
        │
        ▼
Official Public Keys
```

Therefore:

```text
Attacker Private Key
        │
        ▼
Fake Signature
        │
        ▼
Try verification with
Microsoft Public Key
        │
        ▼
FAIL ✗
```

This leads to the fundamental principle:

```text
Cryptographically Valid
≠
Trusted
```

A token may be correctly signed.

But the application must also verify:

```text
Who signed it?
```

---

# 18. Identity Provider Trust vs Application Authorization

The Identity Provider can establish:

```text
Who authenticated?
```

For example:

```text
Microsoft Entra ID

↓

User:

issuer = Microsoft Entra ID
subject = user-123
```

Your application can then map this to:

```text
Application User

user_id = 42
```

Conceptually:

```text
External Identity

issuer
+
subject

        │
        ▼

user_id

        │
        ▼

Internal Application User
```

Then your application performs authorization.

For example:

```text
user_id = 42

        │
        ▼

Can this user:

Read profile?      ✓
Create project?    ✓
Delete project?    ✗
Manage users?      ✗
```

Therefore:

```text
Identity Provider

Answers:

"Who authenticated?"
```

While:

```text
Your Application

Answers:

"What is this user allowed
to do inside my system?"
```

---

# 19. Identity Provider vs Application Database

Your application might store:

```text
users
```

For example:

```text
users

id
name
created_at
```

And:

```text
user_identities
```

For example:

```text
user_identities

id
user_id
issuer
subject
provider
created_at
```

Conceptually:

```text
Microsoft Entra ID

issuer
+
subject

        │
        ▼

user_identities

        │
        ▼

user_id

        │
        ▼

users
```

This allows the application to separate:

```text
External Authentication
```

from:

```text
Internal User Management
```

---

# 20. A Real Microsoft Entra ID Mental Model

For our laboratory, think about the system like this:

```text
┌─────────────────────────┐
│ Your Application        │
│                         │
│ Trusted Authority       │
│ Client ID               │
│ Redirect URI            │
└────────────┬────────────┘
             │
             │ Discovery
             ▼
┌─────────────────────────┐
│ Microsoft Entra ID      │
│                         │
│ OpenID Configuration    │
└────────────┬────────────┘
             │
             │ Metadata
             ▼
┌─────────────────────────┐
│ issuer                  │
│ authorization_endpoint  │
│ token_endpoint          │
│ jwks_uri                │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Microsoft JWKS          │
│                         │
│ Public Signing Keys     │
└─────────────────────────┘
```

Then during login:

```text
User
 │
 ▼
Microsoft Entra ID
 │
 │ Authenticate
 ▼
Authorization Code
 │
 ▼
Your Application
 │
 │ Exchange code
 ▼
ID Token
 │
 │
 ├── iss
 ├── sub
 ├── aud
 ├── exp
 └── kid
 │
 ▼
Find trusted public key
 │
 ▼
Verify signature
 │
 ▼
Validate claims
 │
 ▼
Trusted Identity
```

---

# 21. Key Takeaways

## Identity Provider

```text
Identity Provider

=

A system that provides
identity-related services.
```

## Authorization Server

```text
OAuth 2.0

Authorization Server

=

Issues tokens after
authentication and authorization.
```

## OpenID Provider

```text
Authorization Server

+

OpenID Connect

=

OpenID Provider
```

## Trust

```text
JWT
does not create trust.

Instead:

Application Configuration
        ↓
Trusted Provider
        ↓
Discovery Document
        ↓
JWKS
        ↓
Public Key
        ↓
Signature Validation
```

## Critical Security Principle

```text
Valid Signature
≠
Automatically Trusted Signature
```

The application must know:

```text
Which provider it trusts.
```

And retrieve signing keys through the trusted provider's configured metadata.

---

# 22. Knowledge Check

## Question 1

What is an Identity Provider?

```text
Answer:

A system that provides
identity-related services,
including authentication
and identity assertions.
```

## Question 2

What is an OpenID Provider?

```text
Answer:

An authorization server that
supports OpenID Connect.
```

## Question 3

Where does an application usually discover the provider's endpoints and signing-key location?

```text
Answer:

The OpenID Connect
Discovery Document.
```

## Question 4

What field identifies the JWKS location?

```text
Answer:

jwks_uri
```

## Question 5

What does `kid` help the application do?

```text
Answer:

Identify which public key
from the trusted JWKS should
be used to verify the signature.
```

## Question 6

Can an attacker create their own key pair and sign a fake JWT?

```text
Answer:

Yes.
```

## Question 7

Why should the application reject that token?

```text
Answer:

Because the attacker's public key
is not part of the trusted Identity
Provider's JWKS.
```

## Question 8

Where does trust begin?

```text
Answer:

Trust begins with the application's
configured trusted provider or authority,
not with the JWT itself.
```

---

# 23. Preview of the Next Lecture

The next lecture is:

```text
docs/02-oauth-flow/01-authorization-request.md
```

We will begin examining the real protocol flow.

The next questions are:

```text
What exactly happens when
the user clicks:

"Sign in with Microsoft"?

What URL does the application create?

What is:

client_id?

redirect_uri?

response_type?

scope?

state?

nonce?
```

Conceptually:

```text
Your Application
        │
        │ Build Authorization Request
        ▼
Microsoft Entra ID
        │
        │ User authenticates
        ▼
Authorization Response
```

We will move from:

```text
"What systems do we trust?"
```

to:

```text
"What exactly does the application
send when authentication begins?"
```

---

# 24. References

This lecture uses standards and official provider documentation as its primary sources.

## 24.1 OpenID Foundation — OpenID Connect Discovery

Defines the OpenID Provider metadata mechanism.

Relevant concepts include:

```text
OpenID Provider Configuration
issuer
authorization_endpoint
token_endpoint
userinfo_endpoint
jwks_uri
```

Source:

https://openid.net/specs/openid-connect-discovery-1_0.html

Relevant concept:

```text
jwks_uri

=

The location of the provider's
JSON Web Key Set used for
signature validation.
```

---

## 24.2 OpenID Foundation — OpenID Connect Core

Defines the core OpenID Connect protocol.

Relevant concepts include:

```text
OpenID Provider
Relying Party
ID Token
Claims
Authentication
Token Validation
```

Source:

https://openid.net/specs/openid-connect-core-1_0.html

---

## 24.3 IETF RFC 6749 — OAuth 2.0 Authorization Framework

Defines OAuth 2.0 roles including:

```text
Resource Owner
Client
Authorization Server
Resource Server
Access Token
Authorization Grant
```

Source:

https://www.rfc-editor.org/rfc/rfc6749.html

---

## 24.4 Microsoft — OpenID Connect on the Microsoft Identity Platform

Documents how Microsoft Entra ID exposes OpenID Connect endpoints.

Includes:

```text
OpenID Configuration
Authorization Endpoint
Token Endpoint
JWKS
Signing Key Metadata
```

Source:

https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc

---

## 24.5 Microsoft — Access Tokens and Signing Keys

Explains Microsoft's token validation model and the relationship between OpenID Connect metadata, `jwks_uri`, and signing keys.

Source:

https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens

---

# 25. Lecture Completion Checklist

Before proceeding, verify that you can explain:

- [ ] What an Identity Provider is.
- [ ] What an Authorization Server is.
- [ ] What an OpenID Provider is.
- [ ] How Microsoft Entra ID performs multiple roles.
- [ ] Why a JWT alone should not be trusted.
- [ ] Where application trust begins.
- [ ] What OpenID Connect Discovery is.
- [ ] What the OpenID Configuration Document contains.
- [ ] What `issuer` means.
- [ ] What `jwks_uri` means.
- [ ] What JWKS is.
- [ ] What `kid` is used for.
- [ ] How an application finds the correct public key.
- [ ] Why an attacker's key is rejected.
- [ ] The difference between external authentication and internal authorization.

If these concepts are clear, continue to:

```text
docs/02-oauth-flow/01-authorization-request.md
```

The next lecture begins the hands-on protocol journey:

```text
User clicks:

"Sign in with Microsoft"

        ↓

Your application constructs
an Authorization Request

        ↓

Microsoft Entra ID receives it
```

From this point onward, we will examine the actual OAuth 2.0 and OpenID Connect flow step by step.
