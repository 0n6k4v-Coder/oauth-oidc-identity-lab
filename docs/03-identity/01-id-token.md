# Lecture 05 — OpenID Connect ID Token

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Identity Token Validation
> **Prerequisite:** Understanding of OAuth 2.0 Authorization Code Flow and the distinction between Access Tokens and ID Tokens

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what an OpenID Connect ID Token is and why it exists.
* Explain how an ID Token differs from an OAuth 2.0 Access Token.
* Understand the relationship between an ID Token and the authenticated End-User.
* Explain the basic structure of an ID Token as a JWT.
* Identify the important ID Token claims.
* Explain the purpose of `iss`, `sub`, `aud`, `exp`, `iat`, and `nonce`.
* Understand how the Client obtains an ID Token through the Authorization Code Flow.
* Explain why an ID Token must be validated before the Client relies on its claims.
* Understand the role of the issuer, audience, signature, and time-based validation.
* Recognize common mistakes when treating an ID Token as an API access credential.

---

# 2. Why Does OpenID Connect Need an ID Token?

OAuth 2.0 provides a mechanism for obtaining authorization to access protected resources.

However, OAuth 2.0 itself does not define a standardized identity token that tells a Client:

```text
Who authenticated?
Which OpenID Provider authenticated them?
For which Client was the authentication performed?
When did the authentication occur?
```

OpenID Connect adds an identity layer on top of OAuth 2.0.

Its purpose is to allow the Client to verify the identity of the End-User based on authentication performed by the OpenID Provider.

The primary artifact used for this purpose is the:

```text
ID Token
```

OpenID Connect Core defines the ID Token as a set of Claims about the authentication of the End-User.

---

# 3. Access Token vs ID Token

This distinction is fundamental.

```text
OAuth 2.0

Access Token
      │
      ▼
Resource Server
      │
      ▼
Protected Resource
```

Whereas:

```text
OpenID Connect

ID Token
      │
      ▼
Client / Relying Party
      │
      ▼
Identity / Authentication Information
```

Therefore:

```text
Access Token
    =
Authorization credential

ID Token
    =
Authentication / identity artifact
```

They may both be represented as JWTs in some deployments, but their purposes are different.

Do not determine what a token means merely by looking at its format.

```text
JWT
 │
 └── Representation format

Access Token
 │
 └── OAuth authorization credential

ID Token
 │
 └── OpenID Connect authentication artifact
```

An ID Token should not normally be sent to an API as a substitute for an Access Token.

---

# 4. Where the ID Token Appears in the Authorization Code Flow

The previous lecture showed:

```text
User
  │
  ▼
Browser
  │
  ▼
Authorization Server
  │
  │ Authorization Code
  ▼
Client
  │
  │ Token Request
  ▼
Token Endpoint
  │
  │ Access Token
  ▼
Client
```

OpenID Connect adds the ID Token:

```text
User
  │
  ▼
Browser
  │
  ▼
OpenID Provider
  │
  │ Authorization Code
  ▼
Client
  │
  │ Token Request
  ▼
Token Endpoint
  │
  ├── Access Token
  │
  └── ID Token
       │
       ▼
     Client
```

The Client receives the ID Token from the Token Endpoint when using the OpenID Connect Authorization Code Flow.

The ID Token represents the authentication event associated with the OpenID Connect request.

---

# 5. What Is an ID Token?

An ID Token is a security token defined by OpenID Connect.

It is represented as a JWT.

Conceptually:

```text
ID Token
   │
   └── JWT
        │
        ├── Header
        ├── Payload / Claims
        └── Signature
```

The Claims communicate information about the authenticated End-User and the authentication event.

A simplified example:

```json
{
  "iss": "https://issuer.example.com",
  "sub": "248289761001",
  "aud": "client-123",
  "exp": 1735689600,
  "iat": 1735686000,
  "nonce": "abc123"
}
```

This is only an illustrative example.

The exact Claims contained in an ID Token depend on the OpenID Connect request and provider configuration.

---

# 6. ID Token as a JWT

OpenID Connect defines the ID Token using JWT-related technologies.

A JWT conceptually contains:

```text
             ID Token
                │
      ┌─────────┴─────────┐
      │                   │
   Header              Claims
      │                   │
      │                   │
      └─────────┬─────────┘
                │
             Signature
```

A compact JWT is commonly represented as:

```text
BASE64URL(header)
.
BASE64URL(payload)
.
BASE64URL(signature)
```

For an ID Token, the JWT is cryptographically protected.

OpenID Connect requires ID Tokens to be signed using JWS.

An ID Token may also be encrypted when encryption is configured.

Therefore:

```text
ID Token
   ↓
JWT
   ↓
JWS signature
   ↓
Optional JWE encryption
```

The common Authorization Code Flow case is a signed ID Token.

---

# 7. Signed Does Not Mean Encrypted

This distinction is important.

A signature provides integrity and authentication of the token's issuer.

It does not make the claims secret.

For example:

```text
Signed JWT

Header ───────────► readable
Claims ───────────► readable
Signature ────────► validates authenticity/integrity
```

Therefore an ID Token should not be assumed to contain confidential information merely because it is signed.

If confidentiality is required, encryption can be used.

Conceptually:

```text
JWS
 │
 └── Integrity / authenticity

JWE
 │
 └── Confidentiality
```

OpenID Connect defines ID Tokens as signed and allows them to additionally be encrypted.

---

# 8. The ID Token Claims

The payload of an ID Token is a JWT Claims Set.

Some Claims are particularly important for validation.

A typical ID Token may contain:

```json
{
  "iss": "https://issuer.example.com",
  "sub": "248289761001",
  "aud": "client-123",
  "exp": 1735689600,
  "iat": 1735686000,
  "nonce": "abc123"
}
```

The most important foundational Claims are:

```text
iss
sub
aud
exp
iat
nonce
```

Other Claims can also appear.

For example:

```text
auth_time
acr
amr
azp
```

The exact set depends on the OpenID Connect flow and requested functionality.

---

# 9. The `iss` Claim — Issuer

`iss` identifies the issuer of the ID Token.

Example:

```json
{
  "iss": "https://login.example.com"
}
```

Conceptually:

```text
iss
 │
 ▼
Who issued this ID Token?
```

The Client must not simply trust whatever `iss` value appears inside the token.

It must compare it against the expected OpenID Provider issuer.

Conceptually:

```text
Expected Issuer
      │
      │ compare
      ▼
ID Token iss
      │
      ├── Match ──► Continue
      │
      └── Mismatch ► Reject
```

OpenID Connect requires the Issuer Identifier to exactly match the `iss` Claim.

This is one of the fundamental protections against accepting a token from an unintended issuer.

---

# 10. The `sub` Claim — Subject

The `sub` Claim identifies the subject of the ID Token.

Example:

```json
{
  "sub": "248289761001"
}
```

Conceptually:

```text
sub
 │
 ▼
Which End-User does this token identify?
```

The value is a locally unique and never reassigned identifier within the Issuer for the Client.

The important concept is:

```text
sub
 ≠
User's display name

sub
 ≠
Email address

sub
 ≠
Human-readable username
```

It is an identifier intended to represent the subject.

Therefore an application can conceptually maintain:

```text
OpenID Provider
      │
      │ iss + sub
      ▼
Application User
```

A common identity key is therefore based on the combination:

```text
iss + sub
```

rather than assuming `sub` alone is globally unique across all issuers.

---

# 11. The `aud` Claim — Audience

The `aud` Claim identifies the intended audience of the ID Token.

For an ID Token:

```text
aud
 │
 ▼
Client / Relying Party
```

Example:

```json
{
  "aud": "client-123"
}
```

The Client must verify that its own `client_id` is an intended audience of the ID Token.

Conceptually:

```text
My client_id
     │
     │ compare
     ▼
ID Token aud
     │
     ├── Valid ──► Continue
     │
     └── Invalid ► Reject
```

If the `aud` Claim is an array, the Client must correctly process the audience according to the OpenID Connect validation rules.

This prevents a Client from accepting an ID Token that was issued for another Client.

---

# 12. The `exp` Claim — Expiration Time

`exp` identifies the expiration time of the ID Token.

Example:

```json
{
  "exp": 1735689600
}
```

The value is a NumericDate.

Conceptually:

```text
Current Time
      │
      │ compare
      ▼
     exp
      │
      ├── Not expired ──► Continue
      │
      └── Expired ─────► Reject
```

An expired ID Token should not be accepted as a valid authentication artifact.

Time validation is therefore part of ID Token validation.

---

# 13. The `iat` Claim — Issued At

`iat` identifies the time at which the JWT was issued.

Example:

```json
{
  "iat": 1735686000
}
```

Conceptually:

```text
iat
 │
 ▼
When was this token issued?
```

It provides temporal context for the token.

Unlike `exp`, it does not by itself mean:

```text
"This token is currently valid."
```

It tells the Client when the token was issued.

Validation rules must consider the complete ID Token rather than treating individual Claims as independent proof of validity.

---

# 14. The `nonce` Claim

The `nonce` Claim is particularly important in OpenID Connect.

The Client can generate a random value:

```text
nonce = RANDOM_VALUE
```

It sends that value in the authentication request.

The OpenID Provider associates it with the resulting ID Token:

```text
Authentication Request
        │
        │ nonce = ABC123
        ▼
OpenID Provider
        │
        │
        ▼
ID Token
        │
        │ nonce = ABC123
        ▼
Client
```

The Client compares:

```text
Expected nonce
      =
ID Token nonce
```

If they do not match:

```text
Reject ID Token
```

The nonce provides a binding between the authentication request and the resulting ID Token and helps protect against replay and token substitution attacks.

The exact requirement for `nonce` depends on the OpenID Connect flow.

---

# 15. Other Important Claims

An ID Token can contain additional Claims.

Examples include:

### `auth_time`

Represents the time when the End-User authentication occurred.

```text
auth_time
    ↓
When was the user authenticated?
```

### `acr`

Authentication Context Class Reference.

```text
acr
    ↓
What authentication context was used?
```

### `amr`

Authentication Methods References.

```text
amr
    ↓
Which authentication methods were used?
```

### `azp`

Authorized Party.

```text
azp
    ↓
Which party was the token issued to?
```

These Claims are not all mandatory in every ID Token.

Their presence and validation requirements depend on the applicable OpenID Connect flow and conditions.

---

# 16. Standard Claims vs Application Claims

OpenID Connect defines standard Claims, but an ID Token can also contain additional Claims.

For example:

```text
Standard OIDC Claims
        │
        ├── iss
        ├── sub
        ├── aud
        ├── exp
        ├── iat
        └── ...
        
Additional Claims
        │
        └── Provider / application specific
```

A Client should not automatically assume that every Claim is standardized.

The meaning of a Claim depends on the specification that defines it.

This is particularly important when working with provider-specific Claims.

---

# 17. How Does the Client Know Which Key to Use?

The ID Token is cryptographically signed.

Therefore the Client needs the issuer's appropriate key to validate the signature.

The conceptual relationship is:

```text
OpenID Provider
      │
      │ Publishes / provides keys
      ▼
JWKS / Discovery
      │
      ▼
Client
      │
      │ Validate ID Token signature
      ▼
ID Token
```

The Client should not simply accept a key supplied by an untrusted token itself.

The trusted relationship begins with the expected issuer and its published configuration/keys.

This connects directly to the security concept discussed earlier:

```text
Issuer
   ↓
Trusted configuration
   ↓
Trusted signing keys
   ↓
Signature validation
```

---

# 18. Signature Validation

The Client must establish that the ID Token was actually issued by the expected OpenID Provider and has not been modified.

Conceptually:

```text
ID Token
    │
    ▼
Read Header
    │
    ├── alg
    └── kid
    │
    ▼
Select trusted key
    │
    ▼
Verify signature
    │
    ├── Valid ──► Continue
    │
    └── Invalid ► Reject
```

The `kid` can help identify the appropriate key, but the Client must obtain and trust the key through the issuer's established configuration.

The token itself does not establish that its own signing key is trustworthy.

---

# 19. Algorithm Validation

A common mistake is:

```text
Read alg from token
      ↓
Use whatever algorithm token requests
      ↓
Accept token
```

This is unsafe.

JWT Best Current Practice requires applications to specify the acceptable algorithms rather than blindly trusting the `alg` value supplied by the JWT.

Conceptually:

```text
Application Policy
      │
      │ Allowed Algorithms
      ▼
JWT alg
      │
      ├── Allowed ──► Continue
      │
      └── Not allowed ► Reject
```

RFC 8725 updates RFC 7519 and provides current security guidance for JWT implementations, including algorithm verification and validation of issuer, subject, and audience.

---

# 20. Complete ID Token Validation

For an ID Token received through the OpenID Connect Authorization Code Flow, validation is not:

```text
Decode JWT
     ↓
Read sub
     ↓
Trust user
```

Instead:

```text
ID Token
    │
    ▼
Decrypt if applicable
    │
    ▼
Validate Issuer
    │
    ▼
Validate Audience
    │
    ▼
Validate Signature
    │
    ▼
Validate Algorithm
    │
    ▼
Validate Time Claims
    │
    ├── exp
    └── iat / applicable timing checks
    │
    ▼
Validate nonce when applicable
    │
    ▼
Validate other required Claims
    │
    ▼
Accept ID Token
```

The exact validation requirements are defined by OpenID Connect Core for the relevant flow.

---

# 21. Decoding Is Not Validation

This is one of the most important implementation concepts.

A JWT can be decoded without possessing the signing key.

For example:

```text
JWT
 │
 ├── Header ──► decode
 │
 ├── Payload ─► decode
 │
 └── Signature
```

Decoding only tells the Client:

```text
"What information is encoded in this token?"
```

It does not prove:

```text
"Who issued this token?"
```

or:

```text
"Has this token been modified?"
```

Therefore:

```text
Decode
  ≠
Validate
```

A Client must perform the required cryptographic and semantic validation before trusting the Claims.

---

# 22. Why `iss + sub` Matters

Suppose two different OpenID Providers issue:

```text
Provider A
iss = https://provider-a.example
sub = 12345
```

and:

```text
Provider B
iss = https://provider-b.example
sub = 12345
```

The same `sub` value does not mean the same identity.

Conceptually:

```text
(issuer A, subject 12345)
          ≠
(issuer B, subject 12345)
```

Therefore an application's external identity mapping can conceptually be:

```text
┌──────────────────────────┐
│ External Identity        │
│                          │
│ issuer                   │
│ subject                  │
└────────────┬─────────────┘
             │
             ▼
       Local User
```

This is why `iss` and `sub` should be understood together when identifying an OpenID Connect subject.

---

# 23. ID Token Is Not a User Database

An ID Token can contain identity information, but it is not a replacement for the application's user database.

For example:

```text
ID Token
   │
   ├── iss
   ├── sub
   ├── aud
   ├── exp
   └── ...
   │
   ▼
Application
   │
   ▼
User Account
```

The application may use the validated external identity:

```text
iss + sub
```

to locate its local account.

The local application can then maintain application-specific data:

```text
Local User
 ├── internal user_id
 ├── preferences
 ├── application roles
 └── application data
```

The ID Token is an authentication artifact, not the application's persistent user record.

---

# 24. ID Token and API Authorization

Consider:

```text
Client
  │
  │ ID Token
  ▼
API
```

This is generally the wrong mental model.

Instead:

```text
Client
  │
  │ Access Token
  ▼
Resource Server / API
```

while:

```text
Client
  │
  │ ID Token
  ▼
Client Application
```

The ID Token communicates authentication information to the Client.

The Access Token is the OAuth credential used to access protected resources.

The API should validate the token type and authorization semantics appropriate to that API.

---

# 25. A Complete ID Token Journey

The complete journey can now be represented as:

```text
User
 │
 ▼
Authorization Request
 │
 │ openid scope
 ▼
OpenID Provider
 │
 │ Authenticate User
 ▼
Authorization Code
 │
 ▼
Client
 │
 │ Token Request
 ▼
Token Endpoint
 │
 ├── Access Token
 │
 └── ID Token
       │
       ▼
    Validate
       │
       ├── iss
       ├── sub
       ├── aud
       ├── exp
       ├── signature
       ├── algorithm
       └── nonce
       │
       ▼
Authentication Established
```

The important transition is:

```text
Authentication Response
        ↓
ID Token
        ↓
Validation
        ↓
Trusted Identity Information
```

---

# 26. Security Mental Model

An ID Token should never be treated as trustworthy merely because it came from a browser redirect or because it looks like a valid JWT.

The Client needs to establish:

```text
Who issued it?
       ↓
iss

Who is it intended for?
       ↓
aud

Who is the subject?
       ↓
sub

Is it authentic?
       ↓
Signature

Is it still valid?
       ↓
exp / time validation

Does it belong to this authentication transaction?
       ↓
nonce
```

This produces a much stronger mental model:

```text
JWT Structure
     +
Trusted Issuer
     +
Trusted Keys
     +
Cryptographic Validation
     +
Claim Validation
     +
Protocol Context
     ↓
Trusted ID Token
```

---

# 27. What Happens When Validation Fails?

The Client should reject the ID Token when required validation fails.

Examples:

```text
Issuer mismatch
       ↓
Reject
```

```text
Audience mismatch
       ↓
Reject
```

```text
Invalid signature
       ↓
Reject
```

```text
Unsupported algorithm
       ↓
Reject
```

```text
Expired token
       ↓
Reject
```

```text
Nonce mismatch
       ↓
Reject
```

The key principle is:

```text
Validation failure
       =
Do not establish authentication from that ID Token
```

---

# 28. ID Token vs JWT vs Access Token

These three concepts should now be kept separate:

| Concept      | What it is                     | Primary purpose                                   |
| ------------ | ------------------------------ | ------------------------------------------------- |
| JWT          | Token representation format    | Represent Claims securely                         |
| ID Token     | OpenID Connect artifact        | Communicate authentication / identity information |
| Access Token | OAuth authorization credential | Access protected resources                        |

The relationship can be:

```text
JWT
 ├── ID Token
 │
 └── Access Token
```

but this does **not** mean:

```text
Every JWT = ID Token
```

or:

```text
Every Access Token = JWT
```

Token meaning comes from the protocol context and validation rules, not merely from the token's serialization format.

---

# 29. Practical Validation Checklist

When implementing an OpenID Connect Client, ask:

```text
[ ] Do I know which issuer I trust?

[ ] Does iss exactly match the expected issuer?

[ ] Does aud contain my client_id?

[ ] Do I validate the ID Token signature?

[ ] Do I use trusted issuer keys?

[ ] Do I restrict acceptable signing algorithms?

[ ] Do I validate exp?

[ ] Do I perform the required time validation?

[ ] Do I validate nonce when required?

[ ] Do I understand which Claims are required for this flow?

[ ] Do I distinguish ID Token from Access Token?

[ ] Do I avoid sending the ID Token to an API as an Access Token?

[ ] Do I map external identity using the appropriate issuer/subject
    relationship rather than assuming sub is globally unique?
```

---

# 30. Knowledge Check

### Question 1

What problem does the ID Token solve that OAuth 2.0 alone does not standardize?

---

### Question 2

What is the primary destination of an ID Token?

```text
A. Resource Server
B. Client / Relying Party
C. Database
D. Authorization Endpoint
```

---

### Question 3

What is the primary purpose of an Access Token?

---

### Question 4

Is every JWT an ID Token?

Explain why.

---

### Question 5

What does the `iss` Claim identify?

---

### Question 6

What does the `sub` Claim identify?

---

### Question 7

Why should an application not assume that `sub` alone is globally unique?

---

### Question 8

What does the `aud` Claim tell the Client?

---

### Question 9

Why is decoding an ID Token insufficient?

---

### Question 10

What is the purpose of the `nonce` Claim?

---

### Question 11

Why must the Client validate the signature of an ID Token?

---

### Question 12

Why should the Client not blindly trust the `alg` value from the JWT?

---

### Question 13

Why should an ID Token normally not be sent to an API as the API's Access Token?

---

### Question 14

Explain the difference between:

```text
JWT
ID Token
Access Token
```

in one coherent explanation.

---

# 31. Lecture Summary

An OpenID Connect ID Token is an authentication artifact issued to the Client.

Its purpose is fundamentally different from an OAuth Access Token.

```text
ID Token
   ↓
Authentication / Identity
   ↓
Client
```

while:

```text
Access Token
   ↓
Authorization
   ↓
Protected Resource
```

An ID Token is represented as a JWT and contains Claims such as:

```text
iss
sub
aud
exp
iat
nonce
```

The Client must not simply decode the token and trust its Claims.

It must validate the token according to OpenID Connect's validation rules and the applicable JWT security requirements.

The core mental model is:

```text
Receive ID Token
       ↓
Identify expected issuer
       ↓
Validate issuer
       ↓
Validate audience
       ↓
Validate signature
       ↓
Validate algorithm
       ↓
Validate time
       ↓
Validate nonce when applicable
       ↓
Trust the resulting identity information
```

The most important distinction to retain is:

```text
ID Token
    =
Who authenticated?

Access Token
    =
What protected resource may the Client access?
```

---

# 32. References

## 32.1 OpenID Connect Core 1.0 incorporating errata set 2

**Authority:** OpenID Foundation

**Status:** Final specification incorporating Errata Set 2.

This is the primary source for this lecture.

Official source:

https://openid.net/specs/openid-connect-core-1_0.html

Relevant sections:

```text
Section 1
Introduction

Section 2
ID Token

Section 3.1
Authentication using the Authorization Code Flow

Section 3.1.3.6
ID Token

Section 3.1.3.7
ID Token Validation

Section 3.1.3.8
Access Token Validation

Section 5.1
Standard Claims

Section 16
Security Considerations
```

The specification defines the ID Token, its Claims, its use in the Authorization Code Flow, and the validation requirements applied by the Client.

---

## 32.2 RFC 7519 — JSON Web Token (JWT)

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Standards Track.

Official source:

https://www.rfc-editor.org/rfc/rfc7519.html

RFC 7519 defines JWT as a compact representation of Claims and provides the underlying JWT terminology and structure used by OpenID Connect.

Important update relationship:

```text
RFC 7519
   │
   ├── Updated by RFC 7797
   │
   └── Updated by RFC 8725
```

Therefore RFC 7519 is used here as the foundational JWT specification rather than being treated as the complete current JWT security guidance.

---

## 32.3 RFC 8725 — JSON Web Token Best Current Practices

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 225)

Official source:

https://www.rfc-editor.org/rfc/rfc8725.html

RFC 8725 explicitly updates RFC 7519 and provides current security guidance for JWT implementation and deployment.

Relevant topics:

```text
Algorithm Verification
Appropriate Algorithm Selection
Cryptographic Validation
Issuer Validation
Subject Validation
Audience Validation
Claim Validation
Explicit Typing
Mutually Exclusive Validation Rules
```

This source is particularly important when discussing why a Client must not blindly trust the JWT's `alg`, issuer, audience, or other Claims.

---

## 32.4 RFC 7515 — JSON Web Signature (JWS)

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Standards Track.

Official source:

https://www.rfc-editor.org/rfc/rfc7515.html

JWS defines the digital signature / MAC representation used by signed JWTs.

OpenID Connect uses JWS for signing ID Tokens.

Relevant concepts:

```text
JWS Protected Header
JWS Payload
JWS Signature
alg
kid
Signature Validation
```

---

## 32.5 Source Update / Currency Check

The relevant source relationships for this lecture were checked before drafting.

```text
OpenID Connect Core 1.0
        │
        └── Current published Core specification used here:
            incorporating Errata Set 2

JWT
        │
        ├── RFC 7519
        │      Foundational JWT specification
        │
        └── RFC 8725
               BCP 225
               Updates RFC 7519
               Current JWT security guidance

JWS
        │
        └── RFC 7515
               Foundational JWS specification
```

The lecture therefore uses:

```text
OpenID Connect Core
        +
JWT foundational specification
        +
JWT Best Current Practice
        +
JWS
```

rather than treating the older JWT specification alone as the complete current security guidance.
