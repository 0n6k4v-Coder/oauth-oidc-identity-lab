# Lecture 02 — The Authorization Code

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Module:** OAuth / OIDC Flow  
> **Level:** Intermediate Foundation  
> **Prerequisite:** Authorization Request and OAuth 2.0 Overview

---

# 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain what an Authorization Code is.
- Explain why an Authorization Server returns a code instead of immediately returning an Access Token.
- Understand how the Authorization Code is delivered to the Client.
- Explain why an Authorization Code must be short-lived and single-use.
- Understand how the Authorization Code is bound to the authorization transaction.
- Explain the relationship between the Authorization Code, `client_id`, and `redirect_uri`.
- Understand how PKCE protects the Authorization Code exchange.
- Distinguish the Authorization Code from an Access Token, ID Token, and Refresh Token.
- Understand the difference between the front channel and the back channel.
- Connect the Authorization Code flow to Microsoft Entra ID.

---

# 2. Where We Are in the Flow

The previous lecture examined the Authorization Request.

```text
Client
  │
  │ Authorization Request
  ▼
Authorization Server
  │
  │ Authenticate User
  │ Obtain Authorization
  ▼
Authorization Response
```

If the request succeeds, the Authorization Server can return an intermediate credential:

```text
Authorization Code
```

The Client has not yet received the final tokens.

---

# 3. What Is an Authorization Code?

The OAuth 2.0 Authorization Code Grant uses an Authorization Code as an intermediate credential. After successful authorization, the Authorization Server issues the code. The Client later presents it to the Token Endpoint to obtain tokens.

```text
Authorization Server
        │
        │ Issues
        ▼
Authorization Code
        │
        │ Presented to
        ▼
Token Endpoint
        │
        ▼
Tokens
```

A critical distinction is:

```text
Authorization Code
        ≠
Access Token
```

The Authorization Code is not used to call a Resource Server. Its primary purpose is to be exchanged at the Token Endpoint.

---

# 4. Why Not Return the Access Token Immediately?

The authorization response commonly travels through a User Agent such as a browser. Passing a final bearer credential directly through that path can create unnecessary exposure through browser history, URL handling, logs, extensions, or other components.

The Authorization Code Flow separates the process:

```text
Step 1 — Front Channel

Authorization Server
        │
        │ Authorization Code
        ▼
Browser / User Agent
        │
        ▼
Client


Step 2 — Token Exchange

Client
        │
        │ Authorization Code
        ▼
Token Endpoint
        │
        ▼
Access Token
ID Token
Optional Refresh Token
```

Modern OAuth security guidance recommends avoiding unnecessarily exposing access tokens in the authorization response and using the Authorization Code flow with appropriate protections such as PKCE.

---

# 5. The Authorization Response

After successful authorization, the Authorization Server redirects the User Agent back to the Client.

A conceptual example:

```text
https://client.example.com/callback
    ?code=AUTHORIZATION_CODE
    &state=STATE_VALUE
```

The Client receives:

```text
code=AUTHORIZATION_CODE
```

If `state` was included in the original request, the Client must verify that the returned value matches the value associated with the authorization transaction.

The Client should not blindly trust callback parameters simply because they arrive at its redirect URI.

---

# 6. Authorization Code vs Access Token

| | Authorization Code | Access Token |
|---|---|---|
| Primary purpose | Obtain tokens | Access protected resources |
| Sent to Resource Server | No | Yes |
| Sent to Token Endpoint | Yes | Normally no |
| Intended lifetime | Very short | Provider-defined |
| Intended use | Code exchange | Resource/API access |
| Reusable | No | Usable according to token validity and policy |

The basic sequence is:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ▼
Access Token
        │
        ▼
Resource Server
```

---

# 7. Short Lifetime

RFC 6749 specifies that an Authorization Code MUST expire shortly after issuance. The specification recommends a maximum lifetime of 10 minutes, while an Authorization Server may choose a shorter period.

```text
Issued
  │
  ├──── Valid ────┐
  │               │
  │               ▼
  │            Exchanged
  │
  ▼
Expired
```

A short lifetime reduces the period in which a leaked code could be useful.

---

# 8. Single Use

An Authorization Code is intended to be used once.

```text
Code: ABC123

First exchange
ABC123 → Valid → Tokens issued

Second exchange
ABC123 → Rejected
```

RFC 6749 requires that a Client not use an Authorization Code more than once. If reuse is detected, the Authorization Server must deny the request and should revoke tokens previously issued based on that code when possible.

This property helps mitigate replay.

---

# 9. The Code Represents an Authorization Transaction

Conceptually, an Authorization Code can be associated with server-side information about the completed authorization transaction.

```text
Authorization Code: ABC123
             │
             ▼
Authorization Transaction
  │
  ├── Client
  ├── Authorization result
  ├── User / Resource Owner context
  ├── Granted authorization
  ├── Redirect URI binding
  ├── PKCE challenge, when used
  └── Expiration and usage state
```

The exact internal implementation is provider-specific. A Client should treat the Authorization Code as an opaque protocol value and must not assume a particular format or attempt to derive identity information from it.

---

# 10. Binding the Code to the Client

The Authorization Code is associated with the Client to which it was issued.

```text
Client A
   │
   │ Authorization Request
   ▼
Authorization Server
   │
   ▼
Code ABC123
   │
   └── Issued for Client A
```

During the Token Request, the Authorization Server validates that the code is being used in the appropriate client context.

```text
Client B
  │
  │ code=ABC123
  ▼
Authorization Server
  │
  ├── Was ABC123 issued for this client?
  │
  ├── Yes → Continue validation
  │
  └── No  → Reject
```

This prevents an Authorization Code from being treated as a universally exchangeable credential.

---

# 11. Binding the Code to the Redirect URI

When the original Authorization Request includes a `redirect_uri`, the Token Request must use the corresponding value as required by RFC 6749.

```text
Authorization Request

redirect_uri=A
       │
       ▼
Authorization Code
       │
       ▼
Token Request

redirect_uri=A
       │
       ▼
Expected relationship verified
```

This preserves an important binding to the original authorization transaction.

---

# 12. Front Channel and Back Channel

The Authorization Code commonly travels through the User Agent:

```text
Authorization Server
        │
        ▼
Browser / User Agent
        │
        ▼
Client
```

This path is commonly called the **front channel**.

After receiving the code, the Client communicates with the Token Endpoint:

```text
Client
   │
   │ HTTPS POST
   ▼
Token Endpoint
```

This direct protocol communication is commonly called the **back channel**.

These terms describe communication paths, not automatic security guarantees. Security depends on controls such as TLS, redirect URI validation, client authentication where applicable, PKCE, and correct protocol validation.

---

# 13. The Token Request

The Client exchanges the Authorization Code at the Token Endpoint.

A conceptual request is:

```text
POST /token

Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=AUTHORIZATION_CODE
&redirect_uri=https://client.example.com/callback
```

Depending on the Client type and Authorization Server configuration, the request may also include Client authentication or PKCE information.

---

# 14. What Does the Token Endpoint Validate?

A simplified conceptual model is:

```text
Token Request
      │
      ▼
Is the Client valid?
      │
      ▼
Is the Authorization Code valid?
      │
      ▼
Has the code expired?
      │
      ▼
Has the code already been used?
      │
      ▼
Was the code issued to this Client?
      │
      ▼
Does redirect_uri match where applicable?
      │
      ▼
Verify PKCE where used
      │
      ▼
Issue Tokens
```

Exact provider implementations vary, but these checks illustrate why a stolen code alone is not necessarily sufficient to complete the exchange.

---

# 15. PKCE — Proof Key for Code Exchange

PKCE protects the Authorization Code exchange by linking the authorization request to the later Token Request.

## Step 1 — Generate a Code Verifier

The Client generates a high-entropy secret:

```text
code_verifier
```

The Client keeps this value.

## Step 2 — Create a Code Challenge

For the `S256` method:

```text
code_verifier
      │
      │ SHA-256
      ▼
Hash
      │
      │ base64url encoding
      ▼
code_challenge
```

The Client sends the challenge in the Authorization Request:

```text
code_challenge=...
code_challenge_method=S256
```

## Step 3 — Authorization Code Is Issued

The Authorization Server associates the challenge with the authorization transaction.

## Step 4 — Exchange the Code

The Client sends:

```text
code=AUTHORIZATION_CODE
code_verifier=ORIGINAL_SECRET
```

The Authorization Server derives the expected challenge and compares it with the challenge associated with the authorization transaction.

```text
Received code_verifier
        │
        ▼
Apply S256
        │
        ▼
Calculated challenge
        │
        ▼
Compare
   │          │
 Match     No match
   │          │
   ▼          ▼
Continue    Reject
```

Therefore:

```text
Stealing the Authorization Code
        ≠
Automatically being able to exchange it
```

An attacker would also need to satisfy applicable validation, including possession of the correct `code_verifier` when PKCE is enforced.

---

# 16. Why `S256`?

RFC 9700, the OAuth 2.0 Security Best Current Practice, recommends PKCE protection and requires support for PKCE by Authorization Servers. Current security guidance favors the `S256` transformation method because it does not expose the original `code_verifier` in the Authorization Request.

```text
code_verifier
      │
      ▼
SHA-256 + base64url
      │
      ▼
code_challenge
```

The Authorization Request contains the derived challenge, while the original verifier is retained for the Token Request.

---

# 17. Authorization Code vs Other Artifacts

| Artifact | Primary Purpose | Sent To |
|---|---|---|
| Authorization Code | Exchange for tokens | Token Endpoint |
| Access Token | Access protected resources | Resource Server |
| ID Token | Communicate authentication and identity claims to the Client | Client |
| Refresh Token | Obtain new tokens according to provider policy | Token Endpoint |

Conceptually:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ├── Access Token
        ├── ID Token
        └── Refresh Token
```

The Refresh Token is optional and depends on the authorization grant, requested permissions, provider behavior, and policy.

---

# 18. OAuth 2.0 vs OpenID Connect at This Step

OAuth 2.0 Authorization Code Flow:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ▼
Access Token
```

OpenID Connect Authorization Code Flow can additionally return an ID Token:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ├── Access Token
        └── ID Token
```

The ID Token is an OpenID Connect artifact that communicates claims about authentication and the End-User to the Client.

---

# 19. Microsoft Entra ID Mapping

In this laboratory, Microsoft Entra ID acts as a real Authorization Server and OpenID Provider.

Conceptually:

```text
Your Application
        │
        │ Authorization Request
        ▼
Microsoft Entra ID
        │
        │ User Authentication
        │ Authorization / Consent
        ▼
Authorization Code
        │
        │ Redirect through User Agent
        ▼
Your Application Callback
```

The application then exchanges the code with the Microsoft identity platform Token Endpoint.

```text
Your Application
        │
        │ code
        │ code_verifier when using PKCE
        │ Client authentication where applicable
        ▼
Microsoft Token Endpoint
        │
        ▼
Token Response
```

The exact endpoint, parameters, and authentication method depend on the registered application and platform configuration.

---

# 20. Full Conceptual Walkthrough

## Step 1 — Prepare the Authorization Request

```text
Client
   │
   ├── Generate state
   ├── Generate nonce for OIDC when applicable
   ├── Generate code_verifier
   └── Generate code_challenge
```

Example:

```text
response_type=code
&client_id=CLIENT_ID
&redirect_uri=https://app.example.com/callback
&scope=openid profile email
&state=STATE_VALUE
&nonce=NONCE_VALUE
&code_challenge=PKCE_CHALLENGE
&code_challenge_method=S256
```

## Step 2 — Authorization Server Processes the Request

```text
Authorization Server
        │
        ├── Validate Client
        ├── Validate Redirect URI
        ├── Authenticate User
        └── Obtain Authorization
```

## Step 3 — Authorization Code Is Issued

```text
ABC123
  │
  ├── Short-lived
  ├── Single-use
  ├── Associated with Client
  ├── Associated with authorization transaction
  └── Associated with PKCE challenge when used
```

## Step 4 — Browser Returns to the Client

```text
https://app.example.com/callback
?code=ABC123
&state=STATE_VALUE
```

The Client verifies `state` before continuing.

## Step 5 — Client Exchanges the Code

```text
POST /token

grant_type=authorization_code
&code=ABC123
&redirect_uri=https://app.example.com/callback
&code_verifier=ORIGINAL_PKCE_SECRET
```

## Step 6 — Tokens Are Issued After Validation

```text
Authorization Code
        │
        ▼
Token Endpoint Validation
        │
        ▼
Access Token
ID Token
Optional Refresh Token
```

---

# 21. Common Misconceptions

## "The Authorization Code is an Access Token"

No.

```text
Authorization Code → exchanged for tokens
Access Token       → accesses protected resources
```

## "An Authorization Code can be stored and reused"

No. It is intended to be short-lived and single-use.

## "PKCE encrypts the Authorization Code"

No. PKCE binds the authorization request to the Token Request through the `code_challenge` and `code_verifier` relationship.

## "The Authorization Code contains the user's identity"

Not necessarily. The Client should treat it as opaque. Identity information in OpenID Connect is communicated through protocol artifacts such as a validated ID Token.

## "If a code is stolen, the attacker automatically wins"

Not necessarily. Proper implementations can apply Client binding, redirect URI validation, short expiration, single-use enforcement, and PKCE. Correct implementation of the complete flow remains essential.

---

# 22. Key Takeaways

```text
Authorization Request
        │
        ▼
User Authentication
        │
        ▼
Authorization Decision
        │
        ▼
Authorization Code
        │
        ├── Short-lived
        ├── Single-use
        ├── Associated with Client
        ├── Associated with authorization transaction
        ├── Related to redirect URI
        └── Protected with PKCE when used
        │
        ▼
Token Endpoint
        │
        ▼
Tokens
```

The essential distinction is:

```text
Authorization Code
        ↓
Intermediate credential for token exchange

Access Token
        ↓
Credential for protected resource access

ID Token
        ↓
OIDC authentication and identity claims for the Client
```

---

# 23. Knowledge Check

### Question 1

What is the primary purpose of an Authorization Code?

```text
Answer:
To be exchanged at the Token Endpoint for tokens.
```

### Question 2

Is an Authorization Code the same as an Access Token?

```text
Answer:
No. The Authorization Code is an intermediate credential; the Access Token is used to access protected resources.
```

### Question 3

Why should an Authorization Code expire quickly?

```text
Answer:
To reduce the period in which a leaked or intercepted code could be useful.
```

### Question 4

Can an Authorization Code normally be exchanged twice?

```text
Answer:
No. It is intended to be single-use.
```

### Question 5

What does PKCE protect?

```text
Answer:
PKCE protects the code exchange by requiring proof of possession of the code_verifier associated with the authorization request.
```

### Question 6

Does PKCE encrypt the Authorization Code?

```text
Answer:
No. It creates a verifiable relationship between the authorization request and the later token exchange.
```

### Question 7

What happens after the Client receives the Authorization Code?

```text
Answer:
The Client sends it to the Token Endpoint, where the Authorization Server validates the request before issuing the appropriate tokens.
```

---

# 24. References

This lecture prioritizes protocol standards and official specifications.

## 24.1 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

Defines the OAuth 2.0 Authorization Code Grant and its core requirements.

Relevant concepts:

```text
Authorization Code
Authorization Response
Token Request
Token Response
Client Binding
Redirect URI Validation
Code Expiration
Single Use
```

Source:

https://www.rfc-editor.org/rfc/rfc6749

Relevant sections:

```text
Section 1.3.1 — Authorization Code
Section 4.1 — Authorization Code Grant
Section 4.1.2 — Authorization Response
Section 4.1.3 — Access Token Request
Section 4.1.4 — Access Token Response
```

## 24.2 IETF RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

Defines PKCE.

Relevant concepts:

```text
code_verifier
code_challenge
code_challenge_method
S256
Authorization Code Interception Protection
```

Source:

https://www.rfc-editor.org/rfc/rfc7636

Relevant sections:

```text
Section 4.1 — Client Creates a Code Verifier
Section 4.2 — Client Creates a Code Challenge
Section 4.3 — Client Sends the Code Challenge
Section 4.5 — Client Sends the Authorization Code and Code Verifier
Section 4.6 — Server Verifies the Code Verifier
```

## 24.3 IETF RFC 9700 — Best Current Practice for OAuth 2.0 Security

Provides current security guidance for OAuth 2.0.

Relevant concepts:

```text
Authorization Code Flow
PKCE
S256
Authorization Code Replay
Authorization Response Security
```

Source:

https://www.rfc-editor.org/rfc/rfc9700

## 24.4 OpenID Connect Core 1.0

Defines the OpenID Connect Authorization Code Flow.

Relevant concepts:

```text
Authorization Code Flow
Authorization Endpoint
Token Endpoint
ID Token
Access Token
Authentication Request
```

Source:

https://openid.net/specs/openid-connect-core-1_0.html

Relevant sections:

```text
Section 3.1 — Authentication using the Authorization Code Flow
Section 3.1.1 — Authorization Code Flow Steps
Section 3.1.2 — Authorization Endpoint
Section 3.1.3 — Token Endpoint
```

## 24.5 IETF RFC 10017 — OAuth 2.0 for Browser-Based Applications

Provides current guidance for browser-based OAuth applications.

Relevant concepts:

```text
Authorization Code Grant
PKCE
Authorization Code Redirect
Redirect URI Matching
CSRF Protection
Browser-Based Public Clients
```

Source:

https://www.rfc-editor.org/rfc/rfc10017

---

# 25. Source Hierarchy Used in This Lecture

```text
Protocol Standards
      │
      ├── RFC 6749
      │     OAuth 2.0 Authorization Framework
      │
      ├── RFC 7636
      │     PKCE
      │
      ├── RFC 9700
      │     OAuth 2.0 Security Best Current Practice
      │
      ├── RFC 10017
      │     OAuth 2.0 for Browser-Based Applications
      │
      └── OpenID Connect Core
                │
                ▼
        Provider Documentation
                │
                ▼
        Microsoft Entra ID
```

> **Use protocol standards to understand why the Authorization Code exists and how the protocol is intended to work. Use provider documentation to understand how a specific provider, such as Microsoft Entra ID, implements and configures that flow.**

---

# 26. Next Lecture

Continue to:

```text
docs/02-oauth-flow/03-token-exchange.md
```

The next lecture will examine:

```text
How does the Client exchange the Authorization Code?

What is the Token Endpoint?

How does Client authentication work?

What is the difference between public and confidential Clients?

How does PKCE verification happen?

What does the Token Response contain?

How are Access Tokens, ID Tokens, and Refresh Tokens issued?
```
