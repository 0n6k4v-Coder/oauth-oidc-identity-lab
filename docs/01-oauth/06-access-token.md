# Lecture 06 — Access Token

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Unit:** OAuth 2.0
> **Prerequisite:** Authorization Code and Token Exchange

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what an OAuth 2.0 Access Token represents.
* Distinguish an Access Token from an Authorization Code.
* Explain the relationship between an Access Token, Client, Authorization Server, and Resource Server.
* Explain how scope, lifetime, and audience constrain an Access Token.
* Distinguish opaque Access Tokens from structured JWT Access Tokens.
* Explain how a Resource Server validates an Access Token.
* Explain the security properties and risks of Bearer Access Tokens.
* Explain why Access Tokens must be protected from disclosure and replay.
* Understand sender-constrained Access Tokens at a conceptual level.
* Distinguish DPoP-bound and mutual-TLS certificate-bound Access Tokens.
* Understand when a Resource Server can validate a token locally and when it needs Token Introspection.
* Apply current OAuth security guidance when designing Access Token handling.

---

# 2. Where the Access Token Fits

The previous lecture covered Token Exchange.

The Authorization Code was exchanged at the Token Endpoint:

```text
Authorization Code
        │
        ▼
   Token Endpoint
        │
        ▼
   Access Token
```

The Access Token is now used by the Client to request a protected resource.

The overall relationship is:

```text
                 Authorization Server
                         │
                         │ issues
                         ▼
                      Client
                         │
                         │ Access Token
                         ▼
                   Resource Server
                         │
                         │ authorize
                         ▼
                  Protected Resource
```

This creates an important separation:

```text
Authorization Server
    =
issues authorization credentials

Resource Server
    =
protects and serves resources
```

The Access Token is the credential that connects these two responsibilities.

RFC 6749 defines an Access Token as a string representing an authorization issued to the Client. It represents attributes such as scope and duration, and is used by the Client to access protected resources.

---

# 3. Access Token vs Authorization Code

These two values must not be confused.

## Authorization Code

The Authorization Code is an intermediate authorization grant.

```text
Authorization Code
        │
        ▼
   Token Endpoint
        │
        ▼
    Access Token
```

It is intended to be redeemed by the Client.

It is not normally presented to the Resource Server.

---

## Access Token

The Access Token is the credential used to access protected resources.

```text
Access Token
     │
     ▼
Resource Server
     │
     ▼
Protected Resource
```

Therefore:

```text
Authorization Code
    =
credential used during token exchange

Access Token
    =
credential used for protected resource access
```

This distinction is fundamental to OAuth architecture.

---

# 4. What an Access Token Represents

An Access Token does not simply mean:

```text
"user is logged in"
```

Instead, it represents an authorization decision.

Conceptually:

```text
Access Token
      │
      ├── Client
      ├── Subject / authorization context
      ├── Scope
      ├── Lifetime
      ├── Resource / audience
      └── Other authorization attributes
```

The exact representation is deployment-dependent.

An Access Token can be:

```text
Opaque
```

or:

```text
Structured
```

RFC 6749 deliberately does not require a particular Access Token format. It may be an opaque identifier or may contain verifiable authorization information.

Therefore:

```text
OAuth Access Token
    ≠
JWT by definition
```

JWT is one possible Access Token representation.

---

# 5. Scope

One of the most important authorization attributes associated with an Access Token is its scope.

For example:

```text
scope = profile.read
```

or:

```text
scope = profile.read profile.write
```

Conceptually:

```text
Client
   │
   │ requests scope
   ▼
Authorization Server
   │
   │ grants approved scope
   ▼
Access Token
   │
   ▼
Resource Server
   │
   │ checks required scope
   ▼
Allow / Deny
```

Suppose an API requires:

```text
profile.read
```

and the Access Token contains:

```text
scope = profile.read
```

The request may satisfy the scope requirement.

But if the token contains only:

```text
scope = profile.write
```

the Resource Server should not treat it as equivalent.

Therefore:

```text
Authentication
    ≠
Authorization
```

An Access Token represents authorization for particular protected resources and operations.

---

# 6. Scope Is Not the Same as Role

A common implementation mistake is treating OAuth scope and application roles as identical concepts.

For example:

```text
scope = profile.read
```

is not necessarily equivalent to:

```text
role = admin
```

Scope generally represents delegated authorization granted to a Client.

Application roles may represent a separate authorization model.

A system may use:

```text
Access Token
   │
   ├── scope
   │
   └── claims / authorization context
          │
          ▼
Application Authorization Policy
```

The Resource Server can combine token information with application-specific policy.

The important principle is:

```text
Token attributes
    =
inputs to authorization

not necessarily
    =
complete application authorization model
```

---

# 7. Lifetime

Access Tokens should have a defined validity period.

Conceptually:

```text
issued_at
    │
    ├──────────── valid ────────────┐
    │                              │
    ▼                              ▼
 Token issued                    expires
```

An expired Access Token must not be accepted as valid authorization.

Shorter token lifetimes reduce the impact of token disclosure.

This is especially important for Bearer Tokens because possession of the token can be sufficient to use it.

RFC 6750 highlights token disclosure and replay as major threats for Bearer Tokens and recommends short-lived tokens to reduce the impact of leakage. Current RFC 9700 security guidance continues to emphasize minimizing the impact of token leakage.

---

# 8. Audience and Resource Binding

An Access Token should be intended for the correct protected resource.

Conceptually:

```text
Access Token
     │
     │ intended for
     ▼
Resource Server A
```

It should not automatically be accepted by:

```text
Resource Server B
```

This is particularly important when multiple Resource Servers exist.

A useful model is:

```text
Authorization Server
        │
        ├── Resource A
        │      └── Token A
        │
        ├── Resource B
        │      └── Token B
        │
        └── Resource C
               └── Token C
```

Modern OAuth deployments can use Resource Indicators to explicitly identify the intended resource.

When JWT Access Tokens are used according to RFC 9068, the Resource Server must reject a token whose `aud` claim does not identify the current Resource Server as a valid audience.

This provides an important security boundary:

```text
Valid Token
    ≠
Valid for every Resource Server
```

---

# 9. Bearer Access Tokens

The most common Access Token usage model is the Bearer Token.

The fundamental property is:

```text
Whoever possesses the token
        ↓
can present the token
        ↓
to access the associated resource
```

No additional cryptographic proof of possession is required.

RFC 6750 defines the Bearer Token model and explicitly describes the security consequence: possession of the token is sufficient to use it.

Therefore:

```text
Bearer Token
    =
possession-based credential
```

This makes token confidentiality extremely important.

---

# 10. Sending a Bearer Token

The preferred method for sending a Bearer Access Token is the HTTP `Authorization` header:

```http
GET /api/profile HTTP/1.1
Host: api.example.com
Authorization: Bearer ACCESS_TOKEN
```

Conceptually:

```text
Client
   │
   │ Authorization: Bearer <token>
   ▼
Resource Server
```

RFC 6750 specifies the `Bearer` authentication scheme and requires Resource Servers supporting Bearer Tokens to support the `Authorization` request header method.

---

# 11. Why Access Tokens Must Not Be Put in URLs

An Access Token should not normally be sent as a URI query parameter.

Avoid:

```http
GET /api/profile?access_token=ACCESS_TOKEN
```

URLs can appear in:

```text
Access logs
Browser history
Monitoring systems
Proxy logs
Analytics systems
Referrer-related data
```

This creates unnecessary token leakage risk.

RFC 6750 explicitly identifies the URI query parameter method as insecure and not recommended because URLs containing tokens are likely to be logged.

The preferred pattern is:

```http
Authorization: Bearer ACCESS_TOKEN
```

---

# 12. TLS Is Mandatory for Token Transport

Access Tokens are credentials.

Therefore:

```text
Access Token
     │
     │ MUST be protected in transit
     ▼
    TLS
```

The Client must use HTTPS when presenting a Bearer Access Token.

The Resource Server must also correctly validate the TLS connection.

RFC 6750 requires TLS for requests using Bearer Tokens and emphasizes certificate validation because interception of the token can result in unauthorized access.

The security model is therefore:

```text
Client
   │
   │ HTTPS
   │ Authorization: Bearer ...
   ▼
Resource Server
```

not:

```text
Client
   │
   │ HTTP
   ▼
Resource Server
```

---

# 13. Access Token Confidentiality

An Access Token must be treated as a credential.

Do not expose it unnecessarily through:

```text
Application logs
URLs
Error messages
Telemetry
Screenshots
Client-side debugging output
Analytics
Public storage
```

A useful engineering rule is:

```text
If an attacker obtains a usable Bearer Token,
assume the attacker can use it.
```

RFC 6749 requires Access Token credentials and confidential token attributes to be protected in transit and storage and shared only with the parties for which the token is valid.

---

# 14. Token Validation Is the Resource Server's Responsibility

Once the Client presents an Access Token, the Resource Server must determine whether it can authorize the request.

Conceptually:

```text
             Access Token
                  │
                  ▼
          Resource Server
                  │
          ┌───────┴────────┐
          │                │
       Valid              Invalid
          │                │
          ▼                ▼
     Authorization       Reject
```

Depending on the token format and architecture, validation may include:

```text
Token authenticity
Token expiration
Token audience
Token scope
Token issuer
Token status
Sender constraint
Application policy
```

The exact checks depend on the token type and deployment.

---

# 15. Opaque Access Tokens

An opaque Access Token is intentionally not meaningful to the Client.

Example:

```text
7Gm4xTq9nKp2...
```

The Client does not need to understand the internal structure.

The Resource Server may validate the token through an Authorization Server.

Conceptually:

```text
Client
   │
   │ opaque token
   ▼
Resource Server
   │
   │ introspection
   ▼
Authorization Server
   │
   │ token metadata
   ▼
Resource Server
```

This model is standardized by RFC 7662.

Token Introspection allows a protected resource to ask the Authorization Server whether a token is currently active and to obtain metadata such as scope and authorization context.

---

# 16. Token Introspection

An introspection request conceptually looks like:

```http
POST /introspect
Content-Type: application/x-www-form-urlencoded

token=ACCESS_TOKEN
```

The Authorization Server can return metadata such as:

```json
{
  "active": true,
  "scope": "profile.read",
  "client_id": "client-123",
  "sub": "user-123"
}
```

The exact response depends on the deployment.

The important property is:

```text
Resource Server
      │
      │ "Is this token active?"
      ▼
Authorization Server
      │
      ▼
Token metadata
```

The introspection endpoint itself must be protected against unauthorized token scanning. RFC 7662 requires authorization for access to the endpoint and requires transport security.

---

# 17. Structured Access Tokens

An Access Token can also contain structured information.

One common format is:

```text
JWT
```

However:

```text
JWT Access Token
    ≠
generic JWT
```

A JWT used as an OAuth Access Token should follow the applicable Access Token profile when interoperability is intended.

RFC 9068 defines a standardized JWT Profile for OAuth 2.0 Access Tokens.

---

# 18. JWT Access Token Profile

RFC 9068 standardizes how JWT Access Tokens can be issued and validated.

A JWT Access Token can contain claims such as:

```text
iss
sub
aud
exp
iat
client_id
scope
```

The exact claim set depends on the profile requirements and deployment.

A conceptual token might look like:

```json
{
  "iss": "https://authorization.example.com",
  "sub": "user-123",
  "aud": "https://api.example.com",
  "exp": 1780000000,
  "iat": 1779996400,
  "scope": "profile.read"
}
```

The important point is that these claims become inputs to Resource Server authorization decisions.

---

# 19. JWT Does Not Mean "Trust the Token"

A dangerous misconception is:

```text
"It's a JWT, therefore it is valid."
```

Incorrect.

The Resource Server must validate the JWT according to the applicable profile.

For RFC 9068 JWT Access Tokens, the Resource Server must validate the signature and relevant claims, including expiration and audience. It must reject an invalid signature and reject a token whose audience does not identify the current Resource Server.

The correct mental model is:

```text
JWT
 │
 ├── Signature validation
 ├── Algorithm validation
 ├── Issuer validation
 ├── Audience validation
 ├── Expiration validation
 └── Authorization checks
 │
 ▼
Accept / Reject
```

---

# 20. The `alg` Problem

A Resource Server must not blindly trust the algorithm indicated by an incoming JWT.

For RFC 9068 JWT Access Tokens:

```text
alg = none
```

must not be accepted.

RFC 9068 requires JWT Access Tokens to be signed and requires Resource Servers to reject tokens using the `none` algorithm.

The broader lesson is:

```text
Never treat an attacker-controlled token header
as a trustworthy authorization policy.
```

The accepted algorithms must be determined by the configured security policy and the applicable specification.

---

# 21. Opaque vs JWT Access Tokens

The two approaches can be summarized as:

| Property                             | Opaque Token                  | JWT Access Token                            |
| ------------------------------------ | ----------------------------- | ------------------------------------------- |
| Client understands structure         | No                            | Usually no                                  |
| Resource Server can validate locally | Not inherently                | Yes, if properly configured                 |
| Authorization Server interaction     | Often required                | Not necessarily                             |
| Revocation visibility                | Easier through central status | More difficult with purely local validation |
| Token content exposed to Client      | Usually no                    | JWT claims are readable unless protected    |
| Standardized profile                 | RFC 7662 for introspection    | RFC 9068                                    |
| Operational complexity               | Centralized                   | Distributed validation                      |

Neither model is universally superior.

The correct choice depends on the system architecture.

---

# 22. Local Validation vs Introspection

Consider two architectures.

## Local Validation

```text
Client
   │
   │ Access Token
   ▼
Resource Server
   │
   │ validate locally
   ▼
Allow / Deny
```

This is particularly useful with properly structured JWT Access Tokens.

---

## Introspection

```text
Client
   │
   │ Access Token
   ▼
Resource Server
   │
   │ introspect
   ▼
Authorization Server
   │
   ▼
Active / Metadata
```

This allows the Authorization Server to provide current token state.

The trade-off is that introspection introduces an additional network dependency.

RFC 7662 explicitly defines introspection as a mechanism for a protected resource to obtain current token state and metadata from the Authorization Server.

---

# 23. Bearer Token Replay

A major weakness of Bearer Tokens is replay.

Suppose:

```text
Client
   │
   │ Access Token
   ▼
Resource Server
```

An attacker steals the token:

```text
Attacker
   │
   │ stolen Access Token
   ▼
Resource Server
```

If the token is a Bearer Token and remains valid, the Resource Server may have no cryptographic evidence that the attacker is not the legitimate Client.

Therefore:

```text
Bearer Token
    +
Token Theft
    ↓
Potential Unauthorized Access
```

RFC 6750 explicitly identifies token replay as a security threat.

---

# 24. Sender-Constrained Access Tokens

Modern OAuth provides mechanisms that reduce the impact of token theft by binding an Access Token to a cryptographic key or TLS client identity.

Conceptually:

```text
Access Token
     +
Key Binding
     ↓
Resource Access
```

The attacker would then need:

```text
stolen token
+
corresponding key material
```

instead of only:

```text
stolen token
```

RFC 9700 recommends sender-constrained tokens for scenarios where stronger protection against token replay is required.

Two important standardized mechanisms are:

```text
DPoP
mTLS certificate-bound tokens
```

---

# 25. DPoP

DPoP stands for:

```text
Demonstrating Proof of Possession
```

RFC 9449 defines an application-level mechanism for sender-constraining OAuth Access Tokens.

The Client owns:

```text
Private Key
    +
Public Key
```

The Access Token is bound to the public key.

When accessing the Resource Server, the Client sends a DPoP proof.

Conceptually:

```text
Client
 │
 ├── Access Token
 │
 └── DPoP Proof
        │
        ▼
Resource Server
        │
        ├── Validate Access Token
        ├── Validate DPoP Proof
        └── Verify Key Binding
```

The attacker who possesses only the Access Token should not be able to successfully replay it without the corresponding private key.

RFC 9449 defines DPoP specifically as a mechanism for sender-constraining Access and Refresh Tokens and detecting replay.

---

# 26. Mutual-TLS Certificate-Bound Access Tokens

Another sender-constrained mechanism is mutual TLS.

Conceptually:

```text
Client
   │
   │ mTLS
   ▼
Resource Server
```

The Access Token is bound to the Client's certificate.

The Resource Server checks:

```text
Presented certificate
        =
certificate bound to token
```

If they do not match:

```text
Reject
```

RFC 8705 defines certificate-bound Access Tokens and requires the protected resource to verify that the certificate used for resource access matches the certificate associated with the token.

---

# 27. Sender-Constrained Does Not Solve Everything

Sender-constrained tokens reduce replay risk.

They do not automatically solve:

```text
XSS
Malicious Client Code
Compromised Application
Stolen Private Key
Endpoint compromise
Authorization policy errors
```

RFC 9700 explicitly notes that sender-constrained tokens are undermined if an attacker obtains both the token and the corresponding key material, such as in some compromised-client or XSS scenarios.

Therefore:

```text
Sender Constraint
    ≠
Complete Security
```

It is one control in a larger security architecture.

---

# 28. Access Token Security Is a Layered Control System

A modern OAuth implementation should not depend on a single control.

Think in layers:

```text
                 Access Token Security
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Transport        Token Design       Presentation
       │                 │                 │
      TLS          Scope / Audience     Authorization
       │            Lifetime            Header
       │            Issuer             No URL
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                  Replay Protection
                         │
                  Bearer / DPoP / mTLS
                         │
                  Resource Validation
                         │
                  Application Policy
```

This is the more useful implementation mindset than simply asking:

```text
"Is the token a JWT?"
```

---

# 29. Access Token Does Not Equal Identity

Another important distinction:

```text
Access Token
    ≠
ID Token
```

An OAuth Access Token primarily represents authorization to access protected resources.

An OpenID Connect ID Token represents authentication information about the authenticated End-User.

Therefore:

```text
Access Token
    → API authorization

ID Token
    → Client authentication result
```

A Client should not use an Access Token as a substitute for an ID Token simply because both may be encoded as JWTs.

---

# 30. The Resource Server's Authorization Decision

A Resource Server should not merely ask:

```text
"Is this token syntactically valid?"
```

It should ask:

```text
"Is this request authorized?"
```

A conceptual authorization decision is:

```text
Token
 │
 ├── Valid?
 ├── Issuer?
 ├── Audience?
 ├── Expired?
 ├── Scope?
 ├── Sender constraint?
 │
 ▼
Request Context
 │
 ├── Endpoint
 ├── HTTP method
 └── Application policy
 │
 ▼
Authorization Decision
 │
 ├── Allow
 └── Deny
```

This distinction becomes particularly important when a valid token does not have sufficient authorization for a particular endpoint.

---

# 31. A Valid Token Can Still Be Unauthorized

Consider:

```text
Access Token

scope = profile.read
```

The Client calls:

```http
DELETE /api/profile
```

The token may be:

```text
Valid
```

but the request may still be:

```text
Unauthorized
```

because:

```text
Required scope = profile.delete
Granted scope = profile.read
```

Therefore:

```text
Token validity
    ≠
Request authorization
```

This is one of the most important concepts for Resource Server implementation.

---

# 32. Access Token Error Handling

When a protected resource request contains an invalid or insufficient Access Token, the Resource Server should return an appropriate OAuth error response.

For Bearer Tokens, RFC 6750 defines:

```text
invalid_request
invalid_token
insufficient_scope
```

The Resource Server can communicate the authentication challenge through:

```http
WWW-Authenticate
```

For example:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_token"
```

An authorization failure caused by insufficient scope is conceptually different from a malformed or invalid token.

This distinction is important for both clients and observability.

---

# 33. Cache-Control and Token Responses

Access Token responses contain credentials.

A typical successful token response includes:

```http
Cache-Control: no-store
Pragma: no-cache
```

This reduces the risk of sensitive token responses being stored by intermediary caches.

RFC 6750's token response example uses `Cache-Control: no-store` and `Pragma: no-cache`.

The general security principle is:

```text
Credential response
      ↓
Do not allow unintended caching
```

---

# 34. Access Token Storage

Token storage is an architectural decision.

The correct storage mechanism depends on the Client type.

For example:

```text
Browser-based Client
Native Client
Backend Web Application
Machine-to-Machine Client
```

have different threat models.

There is no universal statement such as:

```text
"Always store tokens in X."
```

Instead, the design must consider:

```text
XSS
CSRF
Token theft
Browser storage exposure
Server compromise
Key protection
Session architecture
```

Modern browser-based OAuth guidance should be consulted when designing browser applications rather than applying generic token-storage advice without considering the Client architecture. RFC 10017 specifically discusses the security limitations of browser-only clients and the role of sender-constrained tokens.

---

# 35. Access Token Lifecycle

The lifecycle can be summarized as:

```text
                 Authorization Server
                         │
                         │ Issue
                         ▼
                    Access Token
                         │
                         │ Store securely
                         ▼
                       Client
                         │
                         │ Present
                         ▼
                  Resource Server
                         │
                         │ Validate
                         ▼
                  Authorization
                         │
              ┌──────────┴──────────┐
              │                     │
             Allow                 Deny
              │
              ▼
       Protected Resource
                         │
                         ▼
                      Expire
```

The token therefore has a lifecycle:

```text
Issue
  ↓
Protect
  ↓
Present
  ↓
Validate
  ↓
Authorize
  ↓
Expire / Revoke
```

---

# 36. Common Implementation Mistakes

## Mistake 1 — Treating Every JWT as an Access Token

```text
JWT
 ↓
Trust
```

Wrong.

The Resource Server must validate the token according to the applicable profile and authorization policy.

---

## Mistake 2 — Checking Only the Signature

```text
signature valid
    ↓
accept
```

Wrong.

A validly signed token can still be:

```text
expired
wrong audience
wrong issuer
insufficient scope
wrong authorization context
```

---

## Mistake 3 — Accepting a Token for Any Audience

```text
Token issued for API A
        ↓
API B accepts it
```

Dangerous.

The Resource Server must ensure that the token is intended for it.

---

## Mistake 4 — Putting Tokens in URLs

```text
/api/profile?access_token=...
```

Avoid this because URLs are highly observable and frequently logged.

---

## Mistake 5 — Logging Tokens

Avoid:

```text
Authorization: Bearer eyJ...
```

in application logs.

A log file can become an unintended credential store.

---

## Mistake 6 — Assuming Short Lifetime Eliminates Replay

Short lifetime reduces the attack window.

It does not eliminate:

```text
token theft
+
immediate replay
```

For higher-risk environments, sender-constrained tokens can provide stronger replay resistance.

---

## Mistake 7 — Confusing Token Validity with Authorization

```text
valid token
    ≠
permission for every endpoint
```

The Resource Server must still evaluate authorization policy.

---

# 37. Mental Model

A useful final model for this lecture is:

```text
                 ACCESS TOKEN
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     Scope         Audience      Lifetime
        │             │             │
        └─────────────┼─────────────┘
                      │
                 Token Type
                      │
              ┌───────┴────────┐
              │                │
           Bearer         Sender-Constrained
              │                │
              │           ┌────┴────┐
              │          DPoP      mTLS
              │
              ▼
        Resource Request
              │
              ▼
        Resource Server
              │
       ┌──────┴──────┐
       │             │
    Validate      Authorize
       │             │
       └──────┬──────┘
              │
         Allow / Deny
```

The key idea is:

```text
Access Token
    =
authorization credential

Resource Server
    =
validation + authorization decision
```

---

# 38. Lecture Summary

An Access Token is an OAuth credential representing authorization to access protected resources.

It is issued by the Authorization Server and presented by the Client to the Resource Server.

The basic flow is:

```text
Authorization Server
        │
        │ issues
        ▼
Access Token
        │
        │ presented by Client
        ▼
Resource Server
        │
        │ validates
        ▼
Authorization Decision
```

Important Access Token properties include:

```text
Scope
Lifetime
Audience / Resource
Token Type
Authorization Context
```

Access Tokens may be:

```text
Opaque
```

or:

```text
Structured
```

A standardized JWT Access Token profile is defined by RFC 9068.

Bearer Tokens are possession-based credentials:

```text
Possession
    →
Potential use
```

Therefore they must be protected from disclosure and replay. RFC 6750 defines their HTTP usage and security considerations.

Modern OAuth security guidance also provides sender-constrained alternatives:

```text
DPoP
mTLS
```

which bind the Access Token to proof of possession of cryptographic material.

The most important distinction is:

```text
Token Validity
      ≠
Authorization
```

A Resource Server must determine not only whether the Access Token is valid, but whether the token authorizes the specific requested resource and operation.

---

# 39. Knowledge Check

1. What does an OAuth Access Token represent?
2. How is an Access Token different from an Authorization Code?
3. Why is an Access Token not necessarily a JWT?
4. What does OAuth scope represent?
5. Why should a Resource Server care about the token audience?
6. What is a Bearer Token?
7. Why is token disclosure especially dangerous for Bearer Tokens?
8. Why should Access Tokens not normally appear in URLs?
9. What is the difference between opaque and JWT Access Tokens?
10. What is Token Introspection?
11. When might a Resource Server perform local JWT validation?
12. Why is a valid JWT signature alone insufficient for authorization?
13. What is the purpose of the `aud` claim?
14. What is the purpose of `exp`?
15. What is the difference between token validity and scope authorization?
16. What problem do sender-constrained tokens address?
17. How does DPoP constrain an Access Token?
18. How does mTLS certificate binding constrain an Access Token?
19. Why does sender constraint not completely eliminate token theft risk?
20. Why should Access Token security be treated as a layered control system?

---

# 40. Standards and Source Fence

> The following sources were checked for applicability and currency before drafting this lecture. Later security guidance is incorporated into the lecture rather than treating the original OAuth 2.0 specification as sufficient on its own.

```text
PRIMARY PROTOCOL FOUNDATION

RFC 6749
The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Relevant:
- Section 1.4 — Access Token
- Section 7 — Access Token
- Section 10.3 — Access Tokens

Important update status:
RFC 6749 has subsequently been updated by RFC 8252,
RFC 8996, and RFC 9700.

Therefore this lecture does not treat RFC 6749 alone
as the complete current security baseline.
```

```text
CURRENT OAUTH SECURITY BASELINE

RFC 9700
Best Current Practice for OAuth 2.0 Security
BCP 240

https://www.rfc-editor.org/rfc/rfc9700.html

This is the primary current security guidance used
to interpret OAuth 2.0 Access Token handling.

It updates and extends the threat model and security
advice from RFC 6749, RFC 6750, and RFC 6819.

Relevant topics:
- Access Token leakage
- Access Token replay
- Sender-constrained tokens
- Secure token handling
- Authorization Code security
- Modern OAuth security architecture
```

```text
BEARER TOKEN USAGE

RFC 6750
OAuth 2.0 Bearer Token Usage

https://www.rfc-editor.org/rfc/rfc6750.html

Relevant topics:
- Authorization: Bearer
- Protected resource requests
- WWW-Authenticate
- invalid_token
- insufficient_scope
- Token disclosure
- Token replay
- TLS
- Avoiding URI query parameters
```

```text
TOKEN INTROSPECTION

RFC 7662
OAuth 2.0 Token Introspection

https://www.rfc-editor.org/rfc/rfc7662.html

Relevant topics:
- active token state
- token metadata
- scope
- authorization context
- Resource Server → Authorization Server validation
- protected introspection endpoint
```

```text
JWT ACCESS TOKEN PROFILE

RFC 9068
JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens

https://www.rfc-editor.org/rfc/rfc9068.html

Relevant topics:
- JWT Access Token profile
- iss
- sub
- aud
- exp
- iat
- scope
- signature validation
- algorithm validation
- Resource Server validation
- application/at+jwt
```

```text
DPoP / SENDER-CONSTRAINED TOKENS

RFC 9449
OAuth 2.0 Demonstrating Proof of Possession (DPoP)

https://www.rfc-editor.org/rfc/rfc9449.html

Relevant topics:
- sender-constrained Access Tokens
- proof of possession
- public/private key pair
- DPoP proof
- replay detection
- binding Access Tokens to a public key
```

```text
MUTUAL-TLS / CERTIFICATE-BOUND TOKENS

RFC 8705
OAuth 2.0 Mutual-TLS Client Authentication and
Certificate-Bound Access Tokens

https://www.rfc-editor.org/rfc/rfc8705.html

Relevant topics:
- certificate-bound Access Tokens
- mutual TLS
- proof of possession
- Resource Server certificate verification
- token/certificate binding
```

```text
BROWSER-BASED APPLICATIONS

RFC 10017
OAuth 2.0 for Browser-Based Applications

https://www.rfc-editor.org/rfc/rfc10017.html

Relevant topics:
- browser-based OAuth threat model
- token exposure
- sender-constrained tokens
- DPoP in browser-compatible architectures
- limitations of browser-only clients
```

> **Source hierarchy for this lecture**

```text
RFC 6749
   │
   │ OAuth 2.0 foundation
   ▼
RFC 6750
   │
   │ Bearer Token usage
   ▼
RFC 7662 / RFC 9068
   │
   │ Token validation models
   ▼
RFC 8705 / RFC 9449
   │
   │ Sender-constrained tokens
   ▼
RFC 9700
   │
   │ Current OAuth 2.0 Security BCP
   ▼
Modern Access Token Security Baseline
```

The practical interpretation for this lecture is therefore:

```text
Access Token
     │
     ├── Scope
     ├── Audience / Resource
     ├── Lifetime
     ├── Token Type
     │
     ├── Bearer
     │
     └── Sender-Constrained
            ├── DPoP
            └── mTLS
     │
     ▼
Resource Server
     │
     ├── Validate
     ├── Authenticate token context
     ├── Check audience
     ├── Check lifetime
     ├── Check scope
     ├── Check sender constraint
     └── Apply application authorization
     │
     ▼
Allow / Deny
```

This reflects the current standards-based model rather than treating the historical RFC 6749/RFC 6750 Bearer Token flow as the complete modern OAuth security model.