# Lecture 05 — OAuth 2.0 Token Exchange

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Token Issuance
> **Prerequisite:** Understanding of the Authorization Request and Authorization Code

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what happens when an Authorization Code is exchanged at the Token Endpoint.
* Distinguish the Authorization Endpoint from the Token Endpoint.
* Explain the purpose of `grant_type=authorization_code`.
* Identify the parameters used in an Authorization Code token request.
* Explain how the Authorization Server validates a token request before issuing tokens.
* Understand how `redirect_uri` participates in token-request validation.
* Understand how client authentication applies to the Token Endpoint.
* Explain how PKCE extends the token exchange with `code_verifier`.
* Understand why Authorization Code reuse must be prevented.
* Identify the conditions under which a Token Endpoint must reject a request.
* Explain why the Token Endpoint is a security-critical back-channel operation.
* Understand how current OAuth security guidance changes the interpretation of the original OAuth 2.0 token exchange.

---

# 2. Where Token Exchange Fits

The previous lecture ended with the Client receiving an Authorization Code.

At that point:

```text
Client
  │
  │ Authorization Code
  ▼
Client
```

The Client does not send that Authorization Code to the Resource Server.

Instead, it exchanges the code at the Authorization Server's Token Endpoint:

```text
Client
  │
  │ Authorization Code
  │
  ▼
Token Endpoint
  │
  │ Validate
  │
  ▼
Authorization Server
  │
  │ Token Response
  ▼
Client
```

The resulting token can then be used in a later resource request.

The fundamental sequence is:

```text
Authorization Endpoint
        ↓
Authorization Code
        ↓
Token Endpoint
        ↓
Token Response
```

---

# 3. Authorization Endpoint vs Token Endpoint

These two endpoints perform different protocol operations.

## Authorization Endpoint

The Authorization Endpoint is where the Client obtains authorization through interaction involving the Resource Owner's user agent.

Conceptually:

```text
Client
   ↓
Browser
   ↓
Authorization Endpoint
```

The result of the Authorization Code flow is an Authorization Code.

---

## Token Endpoint

The Token Endpoint is where the Client presents an authorization grant to obtain an Access Token.

Conceptually:

```text
Client
   │
   │ Token Request
   ▼
Token Endpoint
   │
   │ Validate
   ▼
Token Response
```

The Token Endpoint is therefore the location where the authorization grant is converted into tokens.

RFC 6749 defines the Token Endpoint as the endpoint used by the Client to obtain an Access Token by presenting an authorization grant or a Refresh Token. For the Authorization Code Grant, the Client sends the authorization code to this endpoint. :contentReference[oaicite:1]{index=1}

---

# 4. What Does "Token Exchange" Mean?

In this lecture, Token Exchange means:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

The word "exchange" should not be interpreted as:

```text
Code
    ⇄
Token
```

as if the Client automatically receives a token merely by presenting the code.

The Authorization Server must first establish that the request is valid.

Conceptually:

```text
Authorization Code
        │
        ▼
Token Request
        │
        ▼
Validation
        │
   ┌────┴────┐
   │         │
Valid      Invalid
   │         │
   ▼         ▼
Token      Error
Response
```

The Token Endpoint is therefore not simply a token vending machine.

It is a validation boundary.

---

# 5. The Authorization Code Token Request

For the Authorization Code Grant, the Client sends an HTTP POST request to the Token Endpoint.

Conceptually:

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
client_id=CLIENT_ID
```

The exact parameters depend on the Client type and deployment.

The core Authorization Code request uses:

```text
grant_type
code
```

and may require:

```text
redirect_uri
client_id
```

depending on the original authorization request and Client authentication method. RFC 6749 requires `redirect_uri` in the token request when it was included in the original authorization request, with identical values. An unauthenticated Client also sends `client_id` to ensure that the code is not inadvertently accepted for another Client. :contentReference[oaicite:2]{index=2}

---

# 6. Why `grant_type=authorization_code` Exists

The parameter:

```text
grant_type=authorization_code
```

tells the Token Endpoint which authorization grant the Client is presenting.

Conceptually:

```text
grant_type
    │
    ▼
authorization_code
    │
    ▼
"I am presenting an Authorization Code
as my authorization grant."
```

This allows the Token Endpoint to apply the validation rules associated with that grant type.

The Token Endpoint therefore does not interpret every token request identically.

It first determines the requested grant processing context.

---

# 7. What the Authorization Server Must Validate

The Token Endpoint must validate more than the existence of a `code` parameter.

Conceptually:

```text
Token Request
      │
      ▼
┌─────────────────────────────┐
│ Authorization Server        │
│                             │
│ Validate Client             │
│ Validate Authorization Code │
│ Validate Redirect URI       │
│ Validate PKCE if applicable │
│ Validate grant conditions   │
└──────────────┬──────────────┘
               │
          ┌────┴────┐
          │         │
        Valid     Invalid
          │         │
          ▼         ▼
     Issue Tokens   Error
```

RFC 6749 requires the Authorization Server to:

```text
authenticate the Client when required
verify the authorization code
ensure the code was issued to the Client
validate redirect_uri when applicable
```

These checks establish that the token request corresponds to a valid authorization transaction. :contentReference[oaicite:3]{index=3}

---

# 8. The Authorization Code Is Bound to the Transaction

The Authorization Code is not intended to be a generic credential.

It is associated with the authorization transaction.

Conceptually:

```text
Authorization Request
        │
        ├── Client
        ├── Redirect URI
        └── PKCE context
        │
        ▼
Authorization Code
        │
        ▼
Token Request
        │
        ├── Client
        ├── Redirect URI
        └── PKCE verifier
        │
        ▼
Validation
```

The Authorization Server must ensure that the information presented during token exchange is consistent with the authorization transaction from which the code originated.

This is why the Token Endpoint is more than:

```text
code → token
```

It is:

```text
code
+
transaction context
+
client context
+
security bindings
      ↓
validation
      ↓
token issuance
```

---

# 9. `redirect_uri` Validation

The `redirect_uri` parameter can participate in the token request.

If the Client included `redirect_uri` in the authorization request, the Client must send it in the token request, and the value must be identical.

Conceptually:

```text
Authorization Request

redirect_uri =
https://client.example/callback
            │
            ▼
       Authorization Code
            │
            ▼
Token Request

redirect_uri =
https://client.example/callback
```

The Authorization Server checks:

```text
authorization request redirect_uri
            =
token request redirect_uri
```

If they differ:

```text
Reject
```

This prevents a Client from attempting to redeem a code under a different redirect context.

RFC 6749 defines this equality requirement for the Authorization Code Grant. Current OAuth Security BCP also emphasizes exact redirect URI handling as a broader security baseline. :contentReference[oaicite:4]{index=4}

---

# 10. Client Authentication at the Token Endpoint

The Token Endpoint may require the Client to authenticate.

The requirement depends on the Client type and registration.

Conceptually:

```text
Token Request
      │
      ▼
Does this Client require authentication?
      │
   ┌──┴──┐
   │     │
  Yes    No
   │     │
   ▼     ▼
Authenticate
   │
   └──────┬──────┘
          ▼
Continue Validation
```

For confidential Clients or Clients issued client credentials, RFC 6749 requires Client authentication at the Token Endpoint.

Examples of authentication mechanisms can include:

```text
client_secret_basic
client_secret_post
private_key_jwt
```

The actual method is determined by the authorization-server configuration and Client registration.

Authorization Server Metadata can advertise supported token-endpoint authentication methods using:

```text
token_endpoint_auth_methods_supported
```

RFC 8414 defines this metadata field. :contentReference[oaicite:5]{index=5}

---

# 11. Public Clients and Confidential Clients

This distinction matters during Token Exchange.

## Confidential Client

A confidential Client can maintain credentials securely.

Conceptually:

```text
Client
   │
   │ Client Authentication
   ▼
Token Endpoint
```

The Client may use a registered authentication mechanism.

---

## Public Client

A public Client cannot reliably keep a static secret confidential.

Examples include:

```text
Browser-based applications
Native applications
```

Therefore:

```text
client_secret
    ≠
Reliable security boundary
```

Modern OAuth security guidance requires public clients to use PKCE, rather than relying on a static secret embedded in the client. RFC 9700 also recommends PKCE for confidential clients where applicable. :contentReference[oaicite:6]{index=6}

---

# 12. PKCE Extends the Token Exchange

PKCE adds a proof to the token request.

The Client originally creates:

```text
code_verifier
```

and sends a derived:

```text
code_challenge
```

in the authorization request.

Later, during token exchange:

```text
Client
   │
   │ code_verifier
   ▼
Token Endpoint
```

The Authorization Server verifies that the verifier corresponds to the challenge associated with the Authorization Code.

Conceptually:

```text
Authorization Request
        │
        │ code_challenge
        ▼
Authorization Server
        │
        │ bind to code
        ▼
Authorization Code
        │
        ▼
Token Request
        │
        │ code_verifier
        ▼
Authorization Server
        │
        │ verify binding
        ▼
Token Response
```

RFC 7636 defines the code verifier as the value used to correlate the authorization request with the later token request. :contentReference[oaicite:7]{index=7}

---

# 13. Current PKCE Security Requirement

PKCE is no longer merely an optional enhancement to think about for public clients.

RFC 9700 establishes the current security baseline:

```text
Authorization Server
    MUST support PKCE

Public Client
    MUST use PKCE
```

It also requires the Authorization Server to enforce the verifier when a code challenge was associated with the authorization request.

The server must also prevent PKCE downgrade behavior where a token request supplies a verifier even though the authorization request did not establish a corresponding challenge. :contentReference[oaicite:8]{index=8}

For challenge methods that do not expose the verifier in the authorization request, RFC 9700 identifies:

```text
S256
```

as the currently applicable method. :contentReference[oaicite:9]{index=9}

This changes the way the original OAuth 2.0 Authorization Code flow should be implemented today.

The modern mental model is:

```text
Authorization Code
        +
PKCE Binding
        ↓
Token Request
        ↓
Validation
```

rather than treating PKCE as an optional afterthought.

---

# 14. Authorization Code Replay

Authorization Codes are intended to be short-lived and single-use.

The Client must not reuse a code.

Conceptually:

```text
Authorization Code
       │
       ├── First redemption
       │       ↓
       │     Accept
       │
       └── Second redemption
               ↓
             Reject
```

RFC 6749 states that the Client must not use an Authorization Code more than once. If a code is reused, the Authorization Server must deny the request and should revoke previously issued tokens associated with that code when possible. :contentReference[oaicite:10]{index=10}

This means the Token Endpoint participates directly in replay protection.

---

# 15. Why the Token Endpoint Must Use TLS

A Token Request can contain security-sensitive credentials.

For example:

```text
Authorization Code
code_verifier
Client credentials
```

and the response can contain newly issued tokens.

Therefore:

```text
Client
   │
   │ Sensitive credentials
   ▼
Token Endpoint
```

must use secure transport.

RFC 6749 requires the Token Endpoint to require TLS and requires the Client to use HTTP POST for Access Token requests. :contentReference[oaicite:11]{index=11}

The security boundary is therefore:

```text
Client
  │
  │ HTTPS
  ▼
Token Endpoint
```

not:

```text
Client
  │
  │ Plain HTTP
  ▼
Token Endpoint
```

---

# 16. What Happens When Validation Fails?

A Token Request can fail for many reasons.

Examples:

```text
invalid_grant
invalid_client
invalid_request
unauthorized_client
unsupported_grant_type
```

For an Authorization Code request, common causes include:

```text
Invalid authorization code
Expired authorization code
Authorization code already used
Redirect URI mismatch
Client mismatch
Client authentication failure
PKCE verification failure
```

The important behavior is:

```text
Validation Failure
       ↓
No successful token issuance
```

The Client must not interpret a failed token request as successful authorization.

---

# 17. The Token Response

When validation succeeds, the Authorization Server returns a token response.

Conceptually:

```json
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Depending on the authorization-server behavior and applicable flow, additional values may be returned.

The important point for this lecture is:

```text
Token Endpoint
      ↓
Token Response
```

The token response is the result of the exchange.

The exact semantics of each token will be examined in later lectures.

---

# 18. Token Exchange Is Not Token Validation at the Resource Server

Do not confuse these two stages.

### Token Endpoint

```text
Client
   │
   │ Authorization Code
   ▼
Authorization Server
   │
   │ Issue token
   ▼
Client
```

### Resource Server

```text
Client
   │
   │ Access Token
   ▼
Resource Server
   │
   │ Validate authorization
   ▼
Protected Resource
```

The Token Endpoint answers:

```text
"Can this authorization grant be exchanged for a token?"
```

The Resource Server later answers:

```text
"Does this access token authorize this request?"
```

These are different security decisions.

---

# 19. Token Endpoint as a Security Boundary

The Token Endpoint is a high-value security boundary because several sensitive operations meet there:

```text
Authorization Code
Client Authentication
PKCE
Redirect URI Binding
Token Issuance
Replay Detection
```

A useful model is:

```text
Authorization Code
        │
        ├── Client
        ├── Redirect URI
        ├── PKCE
        └── Validity
        │
        ▼
   Token Endpoint
        │
        ▼
Security Validation
        │
   ┌────┴────┐
   │         │
Valid      Invalid
   │         │
   ▼         ▼
Tokens      Error
```

This is why token exchange must be treated as a security-sensitive protocol operation rather than a simple API call.

---

# 20. Current OAuth Security Interpretation

The original OAuth 2.0 specification defines the Token Endpoint and Authorization Code exchange.

However, modern implementations should not interpret RFC 6749 in isolation.

RFC 9700 provides the current OAuth 2.0 Security Best Current Practice.

For Authorization Code implementations, relevant modern guidance includes:

```text
Authorization Code instead of implicit token delivery
PKCE
Exact redirect URI handling
Authorization Code replay protection
Client authentication where applicable
Protection against authorization-code injection
Protection against PKCE downgrade
Secure token handling
```

Therefore:

```text
RFC 6749
    +
RFC 7636
    +
RFC 9700
```

provides a more appropriate modern basis for implementing the Token Exchange stage than RFC 6749 alone. :contentReference[oaicite:12]{index=12}

---

# 21. End-to-End Token Exchange

The complete exchange can now be represented as:

```text
                Authorization Server
                       │
                       │
            Authorization Code issued
                       │
                       ▼
                    Browser
                       │
                       ▼
                     Client
                       │
                       │ POST /token
                       │
                       │ grant_type=authorization_code
                       │ code
                       │ redirect_uri (when required)
                       │ client authentication
                       │ code_verifier
                       ▼
                 Token Endpoint
                       │
                       │ Validate
                       │
                       ├── Client
                       ├── Code
                       ├── Redirect URI
                       ├── PKCE
                       └── Other conditions
                       │
                       ▼
                 Token Response
                       │
                       ├── Access Token
                       └── Other applicable tokens
                       │
                       ▼
                     Client
```

The critical transition is:

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

# 22. What the Client Must Protect

During Token Exchange, the Client handles sensitive transaction data.

The Client must protect:

```text
Authorization Code
code_verifier
Client credentials, when applicable
Token Response
```

A useful rule is:

```text
Do not log sensitive OAuth credentials.
```

For example, avoid logs such as:

```text
Authorization Code: ABC123
code_verifier: SECRET
Access Token: eyJ...
Client Secret: SECRET
```

Production logging should provide useful operational information without exposing credentials.

---

# 23. What the Client Must Not Do

Avoid these patterns.

### Mistake 1 — Send the Authorization Code to the Resource Server

```text
Client
  ↓
Authorization Code
  ↓
Resource Server
```

Wrong.

The code belongs at the Token Endpoint.

---

### Mistake 2 — Skip Client Validation

```text
Receive code
    ↓
Immediately issue token
```

Wrong.

The Authorization Server must validate the token request.

---

### Mistake 3 — Ignore `redirect_uri`

```text
Authorization Request:
redirect_uri = A

Token Request:
redirect_uri = B

Accept
```

Wrong.

When required, the values must match.

---

### Mistake 4 — Accept a Reused Authorization Code

```text
Code
 ↓
First request  → Accept

Same code
 ↓
Second request → Accept
```

Wrong.

Authorization Codes are single-use.

---

### Mistake 5 — Treat PKCE as Optional for Public Clients

```text
Public Client
    ↓
Authorization Code
    ↓
No PKCE
```

This does not reflect the current OAuth Security BCP baseline.

Public Clients must use PKCE. :contentReference[oaicite:13]{index=13}

---

### Mistake 6 — Put Client Secrets in a Browser Application

A browser-based public Client cannot safely keep a static Client Secret.

Therefore:

```text
Browser
    +
client_secret
    ≠
Confidential Client
```

Client type must be determined by the actual security properties of the architecture.

---

# 24. A Useful Validation Model

The Token Endpoint can be mentally modeled as:

```text
                Token Request
                     │
                     ▼
              ┌──────────────┐
              │ Client       │
              │ Validation   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Grant        │
              │ Validation   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Transaction  │
              │ Validation   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ PKCE /       │
              │ Security     │
              └──────┬───────┘
                     │
                ┌────┴────┐
                │         │
              Valid     Invalid
                │         │
                ▼         ▼
          Token Issue    Error
```

The exact checks depend on the Client type, grant type, and deployment.

---

# 25. Knowledge Check

### Question 1

What is the purpose of the Token Endpoint?

### Question 2

Why does the Authorization Code go to the Token Endpoint instead of the Resource Server?

### Question 3

What does:

```text
grant_type=authorization_code
```

tell the Authorization Server?

### Question 4

Which core parameters can appear in an Authorization Code token request?

### Question 5

When must `redirect_uri` be included in the token request?

### Question 6

Why must the Authorization Server validate the Client during token exchange?

### Question 7

What is the purpose of Client authentication at the Token Endpoint?

### Question 8

What is the role of `code_verifier` during token exchange?

### Question 9

Why must an Authorization Code not be reused?

### Question 10

What happens if the `redirect_uri` in the token request does not match the authorization transaction?

### Question 11

Why is TLS required for the Token Endpoint?

### Question 12

How does RFC 9700 change the modern interpretation of PKCE during token exchange?

### Question 13

What is the difference between:

```text
Token Endpoint validation
```

and:

```text
Resource Server token validation
```

### Question 14

Describe the Token Exchange stage from Authorization Code to Token Response in one coherent explanation.

---

# 26. Lecture Summary

Token Exchange is the stage where the Client presents an Authorization Code to the Authorization Server's Token Endpoint.

The basic sequence is:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

The Token Request may involve:

```text
grant_type
code
redirect_uri
client_id
client authentication
code_verifier
```

depending on the Client and deployment.

The Authorization Server must validate the request before issuing tokens.

Important validation relationships include:

```text
Authorization Code
        +
Client
        +
Redirect URI when applicable
        +
PKCE when applicable
        ↓
Valid Token Request
```

Authorization Codes are short-lived and single-use.

The Token Endpoint must use TLS.

Public Clients must use PKCE under current OAuth Security BCP.

The central mental model is:

```text
Authorization Code
        ↓
    Token Endpoint
        ↓
Security Validation
        ↓
   Token Response
```

The most important distinction to retain is:

```text
Authorization Code
    =
Input to Token Exchange

Access Token
    =
Output of successful Token Exchange
```

And:

```text
Token Endpoint
    =
Where the authorization grant is validated and exchanged

Resource Server
    =
Where the resulting Access Token is later used
```

---

# 27. References

## 27.1 RFC 6749 — The OAuth 2.0 Authorization Framework

**Authority:** Internet Engineering Task Force (IETF)

**Role:** Foundational specification for the Authorization Code Grant and Token Endpoint.

Official source:

https://www.rfc-editor.org/rfc/rfc6749.html

Relevant sections:

```text
Section 3.2
Token Endpoint

Section 3.2.1
Client Authentication

Section 4.1
Authorization Code Grant

Section 4.1.3
Access Token Request

Section 4.1.4
Access Token Response

Section 5
Issuing an Access Token

Section 10
Security Considerations
```

RFC 6749 defines the core Token Endpoint semantics, Authorization Code exchange, Client authentication requirements, redirect URI binding, and authorization-code single-use behavior. :contentReference[oaicite:14]{index=14}

---

## 27.2 RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 240).

**Role:** Current OAuth 2.0 security guidance that updates and extends the security interpretation of the original OAuth framework.

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

Relevant topics:

```text
Authorization Code security
PKCE
PKCE downgrade protection
Authorization Code replay
Redirect URI protection
Authorization Code injection
Mix-Up protection
Token security
```

This is the primary current security source used to interpret the Token Exchange stage.

In particular, RFC 9700 requires Authorization Servers to support PKCE, requires public Clients to use it, and requires enforcement of the corresponding verifier at the Token Endpoint when a challenge was used. :contentReference[oaicite:15]{index=15}

---

## 27.3 RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

**Authority:** Internet Engineering Task Force (IETF)

**Role:** Defines PKCE and the relationship between `code_challenge` and `code_verifier`.

Official source:

https://www.rfc-editor.org/rfc/rfc7636.html

Relevant sections:

```text
Section 4
Protocol

Section 4.1
Client Creates a Code Verifier

Section 4.2
Client Creates the Code Challenge

Section 4.5
Client Sends the Authorization Request

Section 4.6
Client Sends the Authorization Code Request
```

RFC 7636 provides the underlying PKCE mechanism used during Token Exchange. :contentReference[oaicite:16]{index=16}

---

## 27.4 RFC 8414 — OAuth 2.0 Authorization Server Metadata

**Authority:** Internet Engineering Task Force (IETF)

**Role:** Defines metadata that can describe the Authorization Server and its Token Endpoint capabilities.

Official source:

https://www.rfc-editor.org/rfc/rfc8414.html

Relevant metadata:

```text
token_endpoint
token_endpoint_auth_methods_supported
code_challenge_methods_supported
grant_types_supported
```

This specification is relevant when a Client discovers how the Authorization Server expects Token Endpoint interaction to be performed. :contentReference[oaicite:17]{index=17}

---

## 27.5 Source Currency / Update Check

The source set for this lecture was checked against current applicable OAuth standards and security guidance.

```text
RFC 6749
    │
    └── OAuth 2.0 protocol foundation
          ↓
RFC 7636
    │
    └── PKCE mechanism
          ↓
RFC 9700
    │
    └── Current OAuth 2.0 Security BCP
          ↓
RFC 8414
    │
    └── Authorization Server metadata
```

The important update is that modern Token Exchange should not be taught as the historical RFC 6749 flow alone.

The current implementation model is:

```text
Authorization Code
        +
Client Validation
        +
Redirect URI Binding
        +
PKCE
        +
Replay Protection
        +
TLS
        ↓
Token Endpoint
        ↓
Token Response
```

RFC 9700 therefore materially affects how the Authorization Code Token Exchange should be understood and implemented today. :contentReference[oaicite:18]{index=18}
