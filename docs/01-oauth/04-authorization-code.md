# Lecture 04 — OAuth 2.0 Authorization Code

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Protocol Security
> **Prerequisite:** Lecture 03 — OAuth 2.0 Authorization Request

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what an Authorization Code is.
* Explain why the Authorization Code is different from an Access Token.
* Trace where the Authorization Code travels during the authorization flow.
* Explain why the Authorization Code is temporary and transaction-bound.
* Understand how the Authorization Code is exchanged at the Token Endpoint.
* Explain how Client identity, redirect URI, and PKCE protect code redemption.
* Understand authorization-code interception, injection, and replay threats.
* Understand the modern security requirements surrounding the Authorization Code Grant.
* Explain why the Authorization Code Flow is preferred over the historical Implicit Grant in modern OAuth deployments.

---

# 2. What Is an Authorization Code?

The Authorization Code is a temporary credential representing an authorization grant.

In the Authorization Code Grant, the Authorization Server returns the code through the authorization response, and the Client later exchanges that code at the Token Endpoint.

Conceptually:

```text
Resource Owner
      │
      │ Authorization
      ▼
Authorization Server
      │
      │ Authorization Code
      ▼
Client
      │
      │ Token Request
      ▼
Authorization Server
      │
      │ Access Token
      ▼
Client
```

The important distinction is:

```text
Authorization Code
    =
Authorization grant used for token acquisition

Access Token
    =
Credential used to access a protected resource
```

RFC 6749 defines the Authorization Code as an authorization grant obtained by using the Authorization Server as an intermediary between the Client and Resource Owner.

---

# 3. Why Does the Code Exist?

The Authorization Code creates a separation between the authorization interaction and token issuance.

Without this separation, an authorization response could directly carry an Access Token:

```text
Authorization Server
        │
        │ Access Token
        ▼
      Browser
        │
        ▼
      Client
```

The Authorization Code Flow instead uses:

```text
Authorization Server
        │
        │ Authorization Code
        ▼
      Browser
        │
        ▼
      Client
        │
        │ Token Request
        ▼
Authorization Server
        │
        │ Access Token
        ▼
      Client
```

The Authorization Code therefore allows the final token issuance to occur at the Token Endpoint rather than exposing the Access Token directly in the authorization response.

Current OAuth Security BCP recommends the Authorization Code response type rather than the historical Implicit Grant because directly returning Access Tokens from the authorization response creates additional leakage and replay risks.

---

# 4. The Authorization Code Is a Different Credential

Consider:

```text
Authorization Code
        ↓
Token Endpoint
```

while:

```text
Access Token
        ↓
Resource Server
```

Therefore:

```text
Authorization Code
        ≠
Access Token
```

Their purposes are different.

The code is used to obtain tokens.

The Access Token is used to access protected resources.

---

# 5. Where Does the Authorization Code Travel?

The Authorization Code is returned through the authorization response.

Conceptually:

```text
Client
  │
  │ Authorization Request
  ▼
User Agent
  │
  ▼
Authorization Server
  │
  │ Authorization Response
  │
  │ code=...
  ▼
User Agent
  │
  ▼
Client
```

The code therefore travels through a browser-mediated or otherwise user-agent-mediated interaction.

This is commonly called the:

```text
Front Channel
```

The subsequent code exchange occurs directly between the Client and Authorization Server:

```text
Client
  │
  │ code
  ▼
Token Endpoint
```

This is commonly called the:

```text
Back Channel
```

---

# 6. The Code Is Not the Final Authorization Credential

A useful mental model is:

```text
Authorization Code
    ↓
"I have an authorization grant
that I can redeem."

Access Token
    ↓
"I have a credential that can
be presented to a Resource Server."
```

The Client should therefore not send:

```text
Authorization Code
```

to the Resource Server.

Instead:

```text
Client
   │
   │ Authorization Code
   ▼
Authorization Server

Client
   │
   │ Access Token
   ▼
Resource Server
```

---

# 7. The Authorization Code Grant

The Authorization Code Grant consists conceptually of two main stages.

### Stage 1 — Authorization

```text
Client
  ↓
Authorization Endpoint
  ↓
Resource Owner
  ↓
Authorization Decision
  ↓
Authorization Code
```

### Stage 2 — Token Acquisition

```text
Client
  ↓
Token Endpoint
  ↓
Authorization Code
  ↓
Access Token
```

Together:

```text
Authorization
      ↓
Authorization Code
      ↓
Token Exchange
      ↓
Access Token
```

RFC 6749 defines these stages in Sections 4.1.1 through 4.1.4.

---

# 8. Why the Authorization Code Is Temporary

The Authorization Code is transmitted through a redirect-based interaction.

This creates opportunities for interception or misuse.

Therefore the code should be treated as:

```text
Temporary
+
Single-purpose
+
Transaction-bound
```

Conceptually:

```text
Authorization Code
       │
       ├── belongs to a transaction
       ├── belongs to a Client
       ├── associated with authorization context
       └── redeemed at the Token Endpoint
```

The code should not become a reusable long-lived credential.

---

# 9. Authorization Code Interception

One important threat is interception.

Suppose:

```text
Authorization Server
        │
        │ code=ABC
        ▼
User Agent
        │
        │ intercepted
        ▼
Attacker
```

The attacker now possesses:

```text
Authorization Code = ABC
```

Without additional protection, the attacker might attempt to redeem it.

This attack was one of the primary motivations for PKCE.

RFC 7636 defines PKCE specifically to mitigate authorization-code interception attacks.

---

# 10. PKCE Binds the Transaction

The Client first creates:

```text
code_verifier
```

It then derives:

```text
code_challenge
```

and includes the challenge in the Authorization Request.

Later, the Client sends the original verifier during code redemption.

Conceptually:

```text
Authorization Request
        │
        │ code_challenge
        ▼
Authorization Server
        │
        │ Authorization Code
        ▼
Client
        │
        │ code_verifier
        ▼
Token Endpoint
        │
        │ Verify relationship
        ▼
Token Issuance
```

An attacker who intercepts only the Authorization Code does not possess the corresponding verifier.

---

# 11. Modern PKCE Requirement

PKCE is no longer merely a native-app technique.

RFC 9700 requires:

```text
Authorization Server
    MUST support PKCE
```

and:

```text
Public Client
    MUST use PKCE
```

For confidential Clients, PKCE is recommended because it provides strong protection against authorization-code misuse and injection.

RFC 9700 also specifies that the PKCE challenge must be transaction-specific and securely bound to the Client and user agent.

Therefore the modern baseline is:

```text
Authorization Code
        +
PKCE
```

rather than treating PKCE as an optional enhancement only for mobile applications.

---

# 12. Why `S256` Is the Modern Choice

PKCE supports different challenge methods.

For modern deployments:

```text
code_challenge_method=S256
```

is the appropriate choice.

Conceptually:

```text
code_verifier
      │
      │ SHA-256
      ▼
code_challenge
```

The reason is that the verifier should not be exposed directly in the authorization request.

RFC 9700 identifies `S256` as the currently appropriate method that does not expose the verifier in the authorization request.

---

# 13. Code Redemption

After receiving the Authorization Code, the Client sends it to the Token Endpoint.

Conceptually:

```http
POST /token

grant_type=authorization_code
code=AUTHORIZATION_CODE
redirect_uri=https://client.example/callback
code_verifier=CODE_VERIFIER
```

Additional Client authentication may also be required depending on the Client type and authorization-server configuration.

The Token Endpoint then validates the request before issuing tokens.

Detailed token-request mechanics belong to the next lecture; here the important concept is:

```text
Authorization Code
        ↓
Token Endpoint
        ↓
Validation
        ↓
Token Issuance
```

---

# 14. What Does the Authorization Server Validate?

The Authorization Server should not simply accept:

```text
code=ABC
```

and issue a token.

It must establish that the code is valid for the current redemption request.

Conceptually:

```text
Token Request
      │
      ▼
┌─────────────────────────────┐
│ Validate Authorization Code │
│ Validate Client             │
│ Validate Redirect URI       │
│ Validate PKCE               │
│ Validate Client Auth        │
│ Validate Grant              │
└─────────────┬───────────────┘
              │
              ▼
        Token Issuance
```

The exact checks depend on the deployment and Client type.

---

# 15. Authorization-Code Injection

A different threat from interception is **authorization-code injection**.

Conceptually:

```text
Attacker
   │
   │ inserts an authorization code
   ▼
Client
   │
   │ accepts unexpected code
   ▼
Token Endpoint
```

If the Client incorrectly treats the injected code as belonging to its own authorization transaction, security can be compromised.

Current OAuth Security BCP explicitly requires Clients to prevent authorization-code injection and misuse. Public Clients use PKCE for this purpose; confidential Clients are recommended to use PKCE as well.

---

# 16. Transaction-Specific Security Data

The Client should not reuse the same PKCE challenge for every authorization.

Bad:

```text
Every transaction
    ↓
code_challenge = SAME_VALUE
```

Correct:

```text
Transaction A
    ↓
code_challenge = unique_A

Transaction B
    ↓
code_challenge = unique_B
```

Current OAuth Security BCP explicitly requires the PKCE challenge, or OIDC nonce where applicable, to be transaction-specific and securely bound to the Client and user agent.

---

# 17. The Role of `state`

Authorization-code security does not remove the need for correct transaction handling.

A Client may use:

```text
state
```

to correlate the authorization response with the authorization request.

Conceptually:

```text
Authorization Request
        │
        │ state=ABC
        ▼
Authorization Server
        │
        │ state=ABC
        ▼
Client
        │
        │ compare
        ▼
Correct transaction?
```

Current OAuth Security BCP requires Clients to prevent CSRF. Depending on the protocol context and available mechanisms, PKCE or `state` can contribute to that protection.

---

# 18. Authorization-Code Replay

Suppose a code has already been redeemed:

```text
Authorization Code
      ↓
First redemption
      ↓
Success
```

An attacker later attempts:

```text
Same Authorization Code
      ↓
Second redemption
      ↓
?
```

The Authorization Server must prevent inappropriate reuse.

The code is therefore not intended to behave like a permanent credential.

This is one reason code lifetime, transaction binding, PKCE, Client binding, and server-side validation all matter together.

---

# 19. Redirect URI Binding

The Authorization Code is associated with the authorization transaction that created it.

That transaction includes the relevant redirect URI.

Conceptually:

```text
Authorization Request
      │
      ├── Client
      ├── Redirect URI
      └── PKCE Context
             │
             ▼
       Authorization Code
```

When redeeming the code, the Authorization Server can verify that the request corresponds to the original transaction.

Current OAuth Security BCP requires exact string matching for registered redirect URIs, except for the specified localhost port behavior of native applications. This reduces authorization-code leakage and contributes to protection against mix-up attacks.

---

# 20. Authorization Server Identification

There is another modern security concern when one Client supports multiple Authorization Servers.

For example:

```text
Client
 ├── Authorization Server A
 └── Authorization Server B
```

The authorization response defined originally by RFC 6749 does not identify which Authorization Server produced it.

An attacker can exploit this ambiguity in a mix-up attack.

RFC 9207 defines the authorization-response parameter:

```text
iss
```

so that the Client can identify the Authorization Server that generated the response.

Conceptually:

```text
Authorization Response
        │
        ├── code
        ├── state
        └── iss
```

The Client can compare the received issuer with the expected issuer.

---

# 21. Mix-Up Protection and Authorization Code

This is relevant to the Authorization Code Flow because the Authorization Code is a credential.

Consider:

```text
Client
   │
   │ intended request
   ▼
Authorization Server A

But response originates from:

Authorization Server B
   │
   │ code=B_CODE
   ▼
Client
```

If the Client mistakenly sends:

```text
B_CODE
```

to:

```text
Authorization Server A
```

the Client may reveal a credential to the wrong authority.

Current OAuth Security BCP therefore requires a mix-up defense when a Client interacts with multiple Authorization Servers. It recommends issuer identification, including the mechanism from RFC 9207.

---

# 22. Native Applications

RFC 8252 applies the Authorization Code Flow specifically to native applications.

The native application:

```text
Native App
    ↓
External User Agent
    ↓
Authorization Server
```

then receives the Authorization Code through a redirect that returns control to the native application.

For public native clients:

```text
PKCE
    =
MUST implement
```

RFC 8252 explicitly requires public native application clients to implement PKCE and requires Authorization Servers to support it for those clients.

This demonstrates an important principle:

```text
Same Authorization Code concept
        +
Different deployment architecture
```

---

# 23. Why the Historical Implicit Grant Is Different

Older OAuth deployments sometimes used:

```text
response_type=token
```

and returned an Access Token directly through the authorization response.

Modern security guidance considers this model less secure because the Access Token is exposed through the redirect-based authorization response.

RFC 9700 therefore says Clients should not use the Implicit Grant or other response types that directly issue Access Tokens in the authorization response, except where the relevant injection and leakage risks are adequately mitigated.

The modern learning model is therefore:

```text
Authorization Request
        ↓
Authorization Code
        ↓
Token Endpoint
        ↓
Access Token
```

rather than:

```text
Authorization Request
        ↓
Access Token in authorization response
```

---

# 24. The Security Model of the Authorization Code

The complete security picture can now be viewed as:

```text
                  Authorization Request
                           │
                           │
                    code_challenge
                           │
                           ▼
                  Authorization Server
                           │
                           │
                    Authorization Code
                           │
                           ▼
                       Client
                           │
                           │
                    code_verifier
                           │
                           ▼
                    Token Endpoint
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Code valid     Client       PKCE valid
                       valid
              │            │            │
              └────────────┼────────────┘
                           ▼
                      Token Issuance
```

Each check protects a different part of the transaction.

---

# 25. Production Perspective

A production implementation should not reduce the Authorization Code Flow to:

```text
Get code
    ↓
Exchange code
```

It should preserve the security context throughout the transaction:

```text
Trusted Client Configuration
        +
Transaction State
        +
Redirect URI
        +
PKCE
        +
Authorization Code
        ↓
Secure Redemption
        ↓
Token Issuance
```

The implementation should also correctly handle failure.

For example:

```text
Invalid Code
Expired Code
Already Redeemed Code
Wrong Client
Wrong Redirect URI
PKCE Failure
Client Authentication Failure
```

Every failed validation must result in appropriate rejection rather than token issuance.

---

# 26. Practical Mental Model

Think of the Authorization Code as:

```text
"Proof that an authorization transaction
successfully reached the authorization stage,
but it is not yet the Access Token."
```

The sequence is:

```text
User Authorization
        ↓
Authorization Code
        ↓
Client Redemption
        ↓
Authorization Server Validation
        ↓
Access Token
```

The most important security concept is:

```text
Authorization Code
    +
Transaction Binding
    +
PKCE
    +
Client / Redirect Validation
        ↓
Secure Token Exchange
```

---

# 27. Knowledge Check

### Question 1

What is an Authorization Code?

### Question 2

Why is an Authorization Code not the same thing as an Access Token?

### Question 3

Why does the Authorization Code travel through the user agent?

### Question 4

Why is it useful to separate the authorization response from final token issuance?

### Question 5

What threat does PKCE primarily address?

### Question 6

Why must the PKCE challenge be transaction-specific?

### Question 7

Why is `S256` the preferred PKCE method?

### Question 8

What does the Authorization Server validate when redeeming a code?

### Question 9

What is authorization-code injection?

### Question 10

Why does redirect URI validation matter during Authorization Code redemption?

### Question 11

What problem does RFC 9207 solve?

### Question 12

Why is the Authorization Code Flow preferred over the historical Implicit Grant in modern OAuth deployments?

### Question 13

How does the Authorization Code Flow differ for public and confidential Clients?

### Question 14

Explain this sequence in your own words:

```text
Authorization
    ↓
Authorization Code
    ↓
PKCE Verification
    ↓
Token Issuance
```

---

# 28. Lecture Summary

The Authorization Code is a temporary authorization grant used by the Client to obtain tokens from the Authorization Server.

The essential sequence is:

```text
Authorization Request
        ↓
Resource Owner Authorization
        ↓
Authorization Code
        ↓
Token Endpoint
        ↓
Access Token
```

The Authorization Code is different from the Access Token:

```text
Authorization Code
    ↓
Token acquisition

Access Token
    ↓
Protected resource access
```

Modern OAuth security strengthens this flow with:

```text
PKCE
Exact Redirect URI Matching
CSRF Protection
Transaction Binding
Authorization-Code Injection Protection
Mix-Up Defense
Secure Transport
```

In particular:

```text
Public Client
    ↓
MUST use PKCE

Authorization Server
    ↓
MUST support PKCE

Confidential Client
    ↓
PKCE is RECOMMENDED
```

The core mental model is:

```text
Authorization Code
       │
       │ temporary
       │ transaction-bound
       │ not an API credential
       ▼
Token Endpoint
       │
       │ validation
       ▼
Access Token
```

The most important principle is:

```text
A Client should never treat
"having an authorization code"
as equivalent to
"having a valid Access Token."
```

---

# 29. References

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Primary source for:
- Authorization Code
- Authorization Code Grant
- Authorization Endpoint
- Token Endpoint
- Authorization Response
- Access Token Request


RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html

Primary source for:
- code_verifier
- code_challenge
- PKCE flow
- Authorization Code interception mitigation


RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Current OAuth security baseline.

Relevant to this lecture:
- Authorization Code security
- PKCE requirements
- PKCE for public clients
- PKCE recommendation for confidential clients
- Transaction-specific PKCE
- Authorization-code injection
- CSRF protection
- Exact redirect URI matching
- Mix-up attack defenses
- Deprecation of insecure / less secure historical modes


RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification
https://www.rfc-editor.org/rfc/rfc9207.html

Defines:
- authorization-response `iss`
- Authorization Server identification
- mix-up attack mitigation


RFC 8252 — OAuth 2.0 for Native Apps
https://www.rfc-editor.org/rfc/rfc8252.html

Relevant to:
- Native applications
- External user-agent
- Authorization Code Flow
- Public native clients
- PKCE


RFC 8414 — OAuth 2.0 Authorization Server Metadata
https://www.rfc-editor.org/rfc/rfc8414.html

Relevant to:
- Authorization Server configuration
- Discovery of supported capabilities
- PKCE capability advertisement
```

---

# 30. Source Update Analysis

```text
RFC 6749
    ↓
Foundational Authorization Code Grant
    │
    ├── Authorization Code
    ├── Authorization Endpoint
    ├── Token Endpoint
    └── Token Request

RFC 7636
    ↓
Adds PKCE
    │
    ├── code_verifier
    └── code_challenge

RFC 8252
    ↓
Applies Authorization Code + PKCE
to native applications

RFC 9207
    ↓
Adds authorization-response issuer identification
for mix-up defense

RFC 9700
    ↓
Current OAuth Security BCP
    │
    ├── Public Clients MUST use PKCE
    ├── Authorization Servers MUST support PKCE
    ├── Confidential Clients SHOULD use PKCE
    ├── PKCE must be transaction-specific
    ├── Exact redirect URI matching
    ├── Authorization-code injection protection
    ├── CSRF protection
    ├── Mix-up defense
    └── Authorization Code preferred over Implicit
```

The lecture therefore does not present the historical RFC 6749 Authorization Code Grant in isolation.

The current model is:

```text
RFC 6749
    +
RFC 7636
    +
RFC 9207
    +
RFC 8252
    +
RFC 9700
        ↓
Modern Authorization Code Flow
```

---

# 31. Lab Connection

The corresponding production-oriented Lab should eventually allow us to observe and implement:

```text
Authorization Request
        ↓
Authorization Code
        ↓
Secure Callback
        ↓
PKCE Verification
        ↓
Token Exchange
        ↓
Access Token
```

The Lab should also verify failure cases such as:

```text
Wrong code_verifier
Wrong redirect_uri
Invalid / reused authorization code
Authorization-code injection
Mix-up scenario
```

The goal is not merely to demonstrate that a code can be exchanged.

The goal is to demonstrate **why the exchange is secure and how the implementation behaves when its security assumptions are violated**.
