# Lecture 05 — OAuth 2.0 Authorization Code Exchange

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Token Issuance
> **Prerequisite:** Understanding of the Authorization Request and Authorization Code

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what happens when an Authorization Code is exchanged at the Token Endpoint.
* Distinguish the Authorization Endpoint from the Token Endpoint.
* Explain the purpose of `grant_type=authorization_code`.
* Construct the conceptual Token Request for the Authorization Code Grant.
* Explain how the Authorization Server validates an Authorization Code exchange.
* Understand the relationship between the Client and the Authorization Code.
* Understand when `redirect_uri` must be included in the Token Request.
* Explain Client authentication at the Token Endpoint.
* Explain how PKCE adds `code_verifier` to the exchange.
* Understand why Authorization Codes must not be reused.
* Identify important Token Endpoint failure conditions.
* Explain why the Token Endpoint is a security-critical back-channel.
* Apply the modern OAuth security requirements that affect Authorization Code exchange.

---

# 2. What This Lecture Means by "Token Exchange"

The term **Token Exchange** can refer to more than one OAuth-related concept.

In this learning track, it means:

```text
Authorization Code
        ↓
Token Request
        ↓
Token Endpoint
        ↓
Token Response
```

This is the Authorization Code Grant defined by RFC 6749.

It should not be confused with:

```text
RFC 8693
OAuth 2.0 Token Exchange
```

RFC 8693 defines a separate OAuth extension for exchanging one security token for another.

This lecture does **not** cover that extension.

The focus here is:

```text
Authorization Code
        ↓
Access Token
```

through the OAuth Token Endpoint.

---

# 3. Where This Stage Fits

The previous lecture introduced the Authorization Request.

The overall flow now becomes:

```text
Resource Owner
      │
      ▼
Authorization Request
      │
      ▼
Authorization Server
      │
      │ Authorization Response
      │
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
      │ Validation
      ▼
Token Response
      │
      ▼
Client
```

The Token Exchange stage therefore sits between:

```text
Authorization
```

and:

```text
Using the resulting Access Token
```

---

# 4. Authorization Endpoint vs Token Endpoint

These endpoints have different responsibilities.

## Authorization Endpoint

The Authorization Endpoint is used to initiate and process the authorization interaction.

```text
Client
   ↓
User Agent
   ↓
Authorization Endpoint
```

The result of the Authorization Code flow is an authorization response containing an Authorization Code.

---

## Token Endpoint

The Token Endpoint is used by the Client to obtain tokens.

```text
Client
   ↓
Token Endpoint
   ↓
Token Response
```

The Client presents the Authorization Code as an authorization grant.

Therefore:

```text
Authorization Endpoint
    =
Authorization interaction

Token Endpoint
    =
Grant redemption and token issuance
```

RFC 6749 defines the Token Endpoint separately from the Authorization Endpoint and defines the Authorization Code Grant as using both stages. :contentReference[oaicite:1]{index=1}

---

# 5. The Authorization Code Is an Authorization Grant

RFC 6749 defines an authorization grant as a credential representing the Resource Owner's authorization that the Client uses to obtain an Access Token.

One defined grant type is:

```text
authorization_code
```

The Authorization Code therefore represents:

```text
Authorization Grant
```

that the Client can redeem at the Token Endpoint.

Conceptually:

```text
Authorization Code
        │
        │ represents
        ▼
Resource Owner authorization
        │
        ▼
Token Endpoint
```

The Authorization Code is therefore not itself the Access Token.

```text
Authorization Code
    ≠
Access Token
```

---

# 6. Why Is There an Authorization Code?

The Authorization Code creates a separation between authorization and token issuance.

Instead of:

```text
Authorization Response
        ↓
Access Token
```

the Authorization Code flow uses:

```text
Authorization Response
        ↓
Authorization Code
        ↓
Token Endpoint
        ↓
Access Token
```

This allows the Client to obtain the final token through a direct interaction with the Token Endpoint.

The modern OAuth security baseline strongly favors this model over returning Access Tokens directly from the authorization response. RFC 9700 recommends against the historical Implicit Grant approach because tokens returned through the authorization response have additional exposure and replay risks. :contentReference[oaicite:2]{index=2}

---

# 7. The Token Request

For the Authorization Code Grant, the Client sends an HTTP POST request to the Token Endpoint.

The request uses:

```text
application/x-www-form-urlencoded
```

as its request-body format.

A simplified example is:

```http
POST /token HTTP/1.1
Host: authorization.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE
```

Depending on the Client and authorization transaction, additional parameters may be required.

RFC 6749 specifies the Token Request parameters and requires the request to use the `application/x-www-form-urlencoded` format. :contentReference[oaicite:3]{index=3}

---

# 8. `grant_type`

The parameter:

```text
grant_type=authorization_code
```

tells the Token Endpoint which grant type the Client is presenting.

Conceptually:

```text
grant_type
      ↓
authorization_code
      ↓
"I am redeeming an Authorization Code."
```

This allows the Authorization Server to apply the validation rules associated with that grant.

The Token Endpoint therefore does not simply receive:

```text
code=...
```

and issue a token.

It first determines how the request must be processed.

---

# 9. The `code` Parameter

The:

```text
code
```

parameter contains the Authorization Code previously issued by the Authorization Server.

Example:

```text
code=abc123
```

Conceptually:

```text
Authorization Response
        │
        │ code=abc123
        ▼
Client
        │
        │ code=abc123
        ▼
Token Endpoint
```

The Authorization Server must determine whether this code is valid for the requesting Client and current transaction.

A Client must treat the code as a sensitive, short-lived credential.

---

# 10. What Does the Authorization Server Validate?

A successful exchange is not based on:

```text
code exists
      ↓
issue token
```

Instead:

```text
Token Request
      ↓
Validate
      │
      ├── Grant
      ├── Client
      ├── Redirect URI
      ├── PKCE
      ├── Client authentication
      └── Other grant conditions
      │
      ├── Valid
      │
      └── Invalid
```

Only after the applicable validation succeeds should the Authorization Server issue tokens.

RFC 6749 defines the basic authorization-code request validation requirements, while RFC 9700 adds current security requirements and attack mitigations that apply to modern deployments. :contentReference[oaicite:4]{index=4}

---

# 11. Client Binding

An Authorization Code is issued to a specific Client.

Conceptually:

```text
Client A
   │
   │ Authorization
   ▼
Authorization Server
   │
   │ Code A
   ▼
Client A
```

The server must not allow:

```text
Client B
   │
   │ Code A
   ▼
Token Endpoint
```

to redeem the code as though it had been issued to Client B.

This binding is part of the security model of the Authorization Code Grant.

---

# 12. Client Authentication

The Token Endpoint may require Client authentication.

For example, a confidential Client may authenticate using a registered mechanism.

Conceptually:

```text
Client
   │
   │ Identity / authentication
   ▼
Token Endpoint
```

The purpose is to establish:

```text
Which Client is making this Token Request?
```

This is different from the Authorization Code itself.

The server may therefore validate:

```text
Client identity
        +
Authorization Code
        ↓
Does this Client have the right
to redeem this code?
```

RFC 6749 requires confidential Clients to authenticate with the Authorization Server when accessing the Token Endpoint, while public Clients cannot rely on a static secret as a secure authentication factor. :contentReference[oaicite:5]{index=5}

---

# 13. Public Client vs Confidential Client

The Client type changes the security model.

## Confidential Client

A confidential Client can protect credentials such as a client authentication secret.

Conceptually:

```text
Confidential Client
        │
        │ Client Authentication
        ▼
Token Endpoint
```

---

## Public Client

A public Client cannot reliably keep a static credential confidential.

Examples include:

```text
Browser-based applications
Native applications
```

Therefore:

```text
Client Secret inside browser code
        ≠
Secure confidential credential
```

Modern OAuth security therefore relies heavily on PKCE for public Clients.

RFC 9700 requires public Clients to use PKCE and requires Authorization Servers to support PKCE. :contentReference[oaicite:6]{index=6}

---

# 14. `redirect_uri` During Token Exchange

`redirect_uri` can participate in the Token Request.

If the Client included a `redirect_uri` in the original Authorization Request, RFC 6749 requires the Client to include it in the Token Request and requires the value to be identical.

Conceptually:

```text
Authorization Request

redirect_uri = A

        ↓

Authorization Code

        ↓

Token Request

redirect_uri = A
```

The server verifies:

```text
Authorization Request redirect_uri
            =
Token Request redirect_uri
```

If the values do not match:

```text
Reject
```

RFC 6749 defines this relationship explicitly. Current OAuth Security BCP also emphasizes strict redirect URI validation as an important security control. :contentReference[oaicite:7]{index=7}

---

# 15. Why Redirect URI Validation Matters Here

The Authorization Code was produced as part of a particular authorization transaction.

If the Client could redeem that code using arbitrary redirect information, the relationship between:

```text
Authorization Request
```

and:

```text
Token Request
```

would become weaker.

Conceptually:

```text
Original Transaction
        │
        ├── Client
        ├── Redirect URI
        └── Authorization Code
              │
              ▼
        Token Request
              │
              ├── Same Client
              └── Same Redirect Context
```

This is part of the transaction-binding model.

RFC 9700 specifically highlights weaknesses caused by insufficient redirect URI validation and notes that incorrect or incomplete validation can enable attacks involving authorization codes. :contentReference[oaicite:8]{index=8}

---

# 16. PKCE Adds a Second Binding

PKCE adds another relationship between the authorization request and the token request.

The Client creates:

```text
code_verifier
```

and derives:

```text
code_challenge
```

The Client sends the challenge during authorization:

```text
Authorization Request
        │
        └── code_challenge
```

Later:

```text
Token Request
        │
        └── code_verifier
```

The Authorization Server recomputes the challenge from the verifier and compares it with the challenge bound to the Authorization Code.

Conceptually:

```text
code_verifier
      │
      │ transformation
      ▼
code_challenge
      │
      │ bound to
      ▼
Authorization Code
      │
      │ later
      ▼
code_verifier
      │
      │ verification
      ▼
Token Endpoint
```

RFC 7636 defines this relationship. :contentReference[oaicite:9]{index=9}

---

# 17. Why PKCE Protects a Stolen Authorization Code

Suppose an attacker obtains:

```text
Authorization Code
```

but does not obtain:

```text
code_verifier
```

The attacker attempts:

```text
Attacker
   │
   │ code
   ▼
Token Endpoint
```

The Token Endpoint requires the verifier associated with the original authorization request.

Without it:

```text
PKCE verification
      ↓
Failure
      ↓
No token
```

This is one of the primary protections PKCE provides.

RFC 9700 explicitly identifies PKCE as a countermeasure against authorization-code interception and authorization-code injection attacks. :contentReference[oaicite:10]{index=10}

---

# 18. Why `S256` Matters

PKCE supports challenge methods.

For modern deployments, the Client should use:

```text
code_challenge_method=S256
```

The conceptual relationship is:

```text
code_verifier
      │
      │ SHA-256
      ▼
code_challenge
```

The important security property is that the verifier is not exposed directly in the authorization request.

RFC 9700 states that Clients should use PKCE methods that do not expose the verifier in the authorization request and identifies `S256` as currently the only such method. :contentReference[oaicite:11]{index=11}

---

# 19. PKCE Downgrade

PKCE introduces another possible attack if the Authorization Server allows the Client or attacker to turn PKCE off.

For example:

```text
Normal Request
      ↓
code_challenge present
      ↓
PKCE enforced
```

but:

```text
Modified Request
      ↓
code_challenge removed
      ↓
Server silently allows request
      ↓
Code created without PKCE binding
```

An attacker may then attempt to redeem the code without possessing the verifier.

This is called a:

```text
PKCE Downgrade Attack
```

RFC 9700 requires Authorization Servers to avoid this downgrade condition and requires PKCE support. It also recommends that Clients determine whether the Authorization Server supports PKCE before relying on it for CSRF protection. :contentReference[oaicite:12]{index=12}

---

# 20. Authorization Code Injection

A different attack is authorization-code injection.

Conceptually:

```text
Attacker
   │
   │ obtains Code A
   ▼
Attacker starts authorization with Client
   │
   │ replaces returned code
   ▼
Client
   │
   │ submits injected Code A
   ▼
Token Endpoint
```

The attacker attempts to make the victim's Client session become associated with the attacker's stolen code.

RFC 9700 identifies this explicitly as an authorization-code injection attack.

PKCE can detect this because:

```text
Injected Code
      │
      │ bound to different challenge
      ▼
Client's code_verifier
      │
      ▼
PKCE mismatch
      ↓
Reject
```

This is one of the reasons PKCE is valuable beyond simple code interception. :contentReference[oaicite:13]{index=13}

---

# 21. Authorization Code Replay

Authorization Codes must not become reusable credentials.

Consider:

```text
Code A
   │
   ├── First redemption → Success
   │
   └── Second redemption → Reject
```

RFC 6749 states that if an Authorization Code is used more than once, the Authorization Server must deny the request and should revoke previously issued tokens associated with the code when possible. :contentReference[oaicite:14]{index=14}

This makes code reuse detection part of the Token Endpoint's security responsibilities.

---

# 22. Short-Lived Authorization Code

Authorization Codes should be short-lived.

The reason is straightforward:

```text
Long-lived Code
      ↓
Larger attack window

Short-lived Code
      ↓
Smaller attack window
```

Even with PKCE and other controls, the Authorization Code should not be treated as a long-lived credential.

The practical model is:

```text
Authorization Code
    =
Temporary transaction credential
```

not:

```text
Authorization Code
    =
Persistent authentication credential
```

---

# 23. The Token Endpoint Is a Back-Channel

The authorization interaction occurs through a user agent.

The token exchange is performed directly by the Client against the Token Endpoint.

Conceptually:

```text
Front Channel

Client
   ↓
Browser
   ↓
Authorization Server
```

followed by:

```text
Back Channel

Client
   ↓
HTTPS
   ↓
Token Endpoint
```

This direct Client-to-Server interaction is important because the Token Request can contain sensitive values such as:

```text
Authorization Code
code_verifier
Client authentication credentials
```

RFC 6749 requires the Token Endpoint to use TLS and requires the token request to use HTTP POST. :contentReference[oaicite:15]{index=15}

---

# 24. Token Request Errors

A Token Endpoint should reject invalid requests rather than issuing tokens.

Common OAuth error values include:

```text
invalid_request
invalid_client
invalid_grant
unauthorized_client
unsupported_grant_type
```

For Authorization Code exchange, relevant failure conditions can include:

```text
Invalid code
Expired code
Already-used code
Wrong Client
Redirect URI mismatch
Client authentication failure
PKCE verification failure
```

The fundamental rule is:

```text
Validation Failure
        ↓
No successful token issuance
```

RFC 6749 defines the standard Token Endpoint error response model. :contentReference[oaicite:16]{index=16}

---

# 25. What `invalid_grant` Means Here

For an Authorization Code exchange, several authorization-grant problems can lead to:

```text
invalid_grant
```

For example:

```text
Authorization Code invalid
Authorization Code expired
Authorization Code already used
Authorization Code issued to another Client
Redirect URI does not match
```

The exact error behavior must follow the applicable OAuth specification and authorization-server implementation.

The important mental model is:

```text
The grant is invalid
        ↓
The Token Endpoint must not turn it into a valid token
```

---

# 26. Successful Token Response

If the request passes all required validation, the Authorization Server returns a Token Response.

A conceptual response is:

```json
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Depending on the authorization server and applicable flow, additional fields may be returned.

The important sequence is:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

The semantics and validation of the resulting Access Token belong to the next part of the learning track.

---

# 27. What the Token Endpoint Does Not Do

The Token Endpoint does not answer:

```text
"May this token access this API?"
```

That is a later Resource Server decision.

The Token Endpoint answers a different question:

```text
"Is this token request valid,
and may this Client receive tokens
for this authorization grant?"
```

Therefore:

```text
Token Endpoint
    =
Grant validation + token issuance

Resource Server
    =
Protected resource authorization
```

Keeping these responsibilities separate is essential.

---

# 28. Token Exchange Security as Defense in Depth

The modern exchange can be viewed as multiple controls:

```text
Authorization Code
        │
        ├── Client binding
        │
        ├── Redirect URI binding
        │
        ├── PKCE
        │
        ├── Client authentication
        │
        ├── Code lifetime
        │
        ├── Single-use enforcement
        │
        └── TLS
        │
        ▼
Token Endpoint
        │
        ▼
Validation
        │
   ┌────┴─────┐
   │          │
 Valid      Invalid
   │          │
   ▼          ▼
Tokens       Error
```

No single control is expected to solve every attack.

Instead:

```text
Multiple Controls
       ↓
Defense in Depth
```

This reflects the security model in RFC 9700. :contentReference[oaicite:17]{index=17}

---

# 29. Authorization Code Exchange — Complete Mental Model

The entire process can now be represented as:

```text
                Authorization Server
                       │
                       │
                 Authorization
                       │
                       ▼
                    Client
                       │
                       │ Authorization Code
                       ▼
                Token Endpoint
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       Client        Code        PKCE
     Validation    Validation   Validation
          │            │            │
          └────────────┼────────────┘
                       │
                 Redirect URI
                   Validation
                       │
                       ▼
                Token Issuance
                       │
                       ▼
                     Client
```

A simpler version is:

```text
Authorization Code
        ↓
Token Request
        ↓
Validate
        ↓
Issue Tokens
```

---

# 30. Production Checklist

Before a Client performs Authorization Code exchange, verify:

```text
[ ] The Token Endpoint is obtained from trusted configuration.

[ ] HTTPS is used.

[ ] grant_type=authorization_code is used.

[ ] The correct Authorization Code is supplied.

[ ] The request is sent using POST.

[ ] application/x-www-form-urlencoded is used.

[ ] Client authentication is performed when required.

[ ] redirect_uri is included when required.

[ ] redirect_uri matches the original authorization transaction.

[ ] code_verifier is supplied when PKCE is used.

[ ] The Client uses S256 for PKCE.

[ ] Authorization Codes are never intentionally reused.

[ ] Authorization Codes are not logged.

[ ] code_verifier is not logged.

[ ] Token responses are handled as sensitive data.

[ ] Token Endpoint errors are handled explicitly.
```

---

# 31. Knowledge Check

### Question 1

What is the purpose of the Token Endpoint?

### Question 2

Why is an Authorization Code not the same thing as an Access Token?

### Question 3

What does `grant_type=authorization_code` indicate?

### Question 4

Why must the Authorization Server bind an Authorization Code to the Client?

### Question 5

When must `redirect_uri` be included in the Token Request?

### Question 6

Why must the `redirect_uri` values match?

### Question 7

What is the purpose of Client authentication at the Token Endpoint?

### Question 8

What problem does PKCE solve during Token Exchange?

### Question 9

Why is `code_verifier` not sent in the original Authorization Request?

### Question 10

Why is `S256` preferred?

### Question 11

What is an authorization-code injection attack?

### Question 12

What is a PKCE downgrade attack?

### Question 13

Why must an Authorization Code be single-use?

### Question 14

Why does the Token Endpoint require TLS?

### Question 15

What is the difference between Token Endpoint validation and Resource Server authorization?

### Question 16

What does `invalid_grant` generally represent during Authorization Code exchange?

### Question 17

Why is Authorization Code exchange considered a back-channel operation?

### Question 18

Explain the complete sequence:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

---

# 32. Lecture Summary

The Authorization Code Exchange is the stage where a Client redeems an Authorization Code at the Authorization Server's Token Endpoint.

The core process is:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

The Token Request identifies:

```text
grant_type=authorization_code
```

and includes the Authorization Code.

Depending on the Client and transaction, it can also include:

```text
redirect_uri
client_id
code_verifier
Client authentication
```

The Authorization Server validates the request before issuing tokens.

Important security controls include:

```text
Client Binding
Redirect URI Binding
PKCE
Client Authentication
Single-Use Authorization Codes
Short Code Lifetime
TLS
Replay Protection
```

Modern OAuth security changes the baseline substantially:

```text
Public Client
    ↓
PKCE required

Authorization Server
    ↓
PKCE support required

PKCE
    ↓
S256 preferred

Authorization Code
    ↓
Must be protected against interception,
injection, and replay
```

RFC 9700 is therefore essential when interpreting the original Authorization Code Grant for modern deployments. :contentReference[oaicite:18]{index=18}

The key distinction to retain is:

```text
Authorization Code
    =
Temporary authorization grant

Token Request
    =
Request to redeem that grant

Token Response
    =
Result of successful validation

Access Token
    =
Credential used later with a Resource Server
```

Therefore:

```text
Authorization Endpoint
        ↓
Authorization Code
        ↓
Token Endpoint
        ↓
Token Response
        ↓
Resource Server
```

---

# 33. References

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Primary source for:
- Authorization Code Grant
- Token Endpoint
- Access Token Request
- Access Token Response
- Client Authentication
- Redirect URI matching
- Authorization Code reuse
- Token Endpoint errors
- TLS requirements


RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html

Primary source for:
- code_verifier
- code_challenge
- code_challenge_method
- PKCE token request verification


RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Current OAuth Security BCP.

Relevant to this lecture:
- PKCE requirements
- Public Client requirements
- S256
- Authorization Code interception
- Authorization Code injection
- PKCE downgrade attacks
- Redirect URI protection
- Authorization Code replay protection
- Modern Authorization Code security


RFC 8414 — OAuth 2.0 Authorization Server Metadata
https://www.rfc-editor.org/rfc/rfc8414.html

Relevant to discovering:
- token_endpoint
- token endpoint authentication methods
- supported grant types
- supported PKCE challenge methods


RFC 8693 — OAuth 2.0 Token Exchange
https://www.rfc-editor.org/rfc/rfc8693.html

Important terminology distinction only.

This lecture does NOT cover RFC 8693.
RFC 8693 defines a separate OAuth Token Exchange extension.
This lecture uses "Token Exchange" to describe
Authorization Code redemption at the Token Endpoint.
```

---

# 34. Source Currency / Update Check

The relevant specifications were checked before drafting.

```text
RFC 6749
    │
    └── Foundational OAuth 2.0 Authorization Code Grant
            │
            ▼
RFC 7636
    │
    └── Adds PKCE
            │
            ▼
RFC 9700
    │
    └── Current OAuth Security BCP
            │
            ├── Public Clients MUST use PKCE
            ├── Authorization Servers MUST support PKCE
            ├── S256 is the preferred method
            ├── Authorization Code injection protection
            ├── PKCE downgrade protection
            ├── Redirect URI security
            └── Replay protection
            │
            ▼
RFC 8414
    │
    └── Authorization Server Metadata
```

The most important update affecting this lecture is that the historical Authorization Code Grant from RFC 6749 should not be implemented today without the security guidance from RFC 9700.

Therefore the modern model is:

```text
RFC 6749
    +
RFC 7636
    +
RFC 9700
        ↓
Modern Authorization Code Exchange
```

The separate RFC 8693 Token Exchange extension is explicitly outside this lecture's scope.
