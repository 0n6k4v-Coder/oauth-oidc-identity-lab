# Lecture 03 — OAuth 2.0 Authorization Request

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Protocol Interaction
> **Prerequisite:** Lecture 01 — OAuth 2.0 Overview; Lecture 02 — OAuth 2.0 Roles

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what an OAuth Authorization Request is.
* Identify the Authorization Endpoint and understand its role.
* Explain the purpose of the major Authorization Request parameters.
* Distinguish the Client's request from the user's authorization decision.
* Understand how the user agent carries the authorization request.
* Understand why the `redirect_uri` is a security-critical parameter.
* Understand the role of `state` in correlating an authorization request and response.
* Understand where PKCE enters the authorization request.
* Understand how modern OAuth security guidance changes the way authorization requests should be constructed and validated.
* Recognize the authorization request as the beginning of a larger authorization transaction rather than an isolated HTTP request.

---

# 2. Where the Authorization Request Begins

The Client has determined that it needs authorization to access a protected resource.

The next step is to initiate an authorization transaction with the Authorization Server.

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
```

The Authorization Request is therefore the mechanism by which the Client asks the Authorization Server to begin the authorization process.

In the Authorization Code Grant, the request is directed to the Authorization Endpoint.

RFC 6749 defines the Authorization Endpoint as the endpoint used by the Client to obtain authorization from the Resource Owner through a user-agent redirection.

---

# 3. Authorization Request Is Not the Authorization Decision

This distinction is important.

The Client creates the request:

```text
Client
   │
   │ "I am requesting authorization."
   ▼
Authorization Server
```

But the request itself does not mean that authorization has already been granted.

The Authorization Server may:

```text
Accept the request
     ↓
Authenticate the Resource Owner
     ↓
Ask for authorization
     ↓
Grant or deny access
```

Therefore:

```text
Authorization Request
    ≠
Authorization Decision
```

The request establishes the context in which the authorization decision will be made.

---

# 4. The Authorization Endpoint

The Authorization Endpoint is the location to which the Client directs the Resource Owner's user agent.

For example:

```text
https://authorization.example.com/authorize
```

Conceptually:

```text
Client
  │
  │ Construct authorization request
  ▼
Browser
  │
  │ Navigate
  ▼
Authorization Endpoint
```

The Authorization Endpoint is therefore primarily a **user-agent-facing protocol endpoint**.

It is not the Token Endpoint.

The Token Endpoint is used later for token issuance.

---

# 5. A Simplified Authorization Request

A conceptual Authorization Request for an Authorization Code flow may look like:

```http
GET /authorize?
    response_type=code&
    client_id=client-123&
    redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
    scope=read&
    state=abc123&
    code_challenge=XYZ...&
    code_challenge_method=S256
HTTP/1.1
Host: authorization.example.com
```

The exact parameter set depends on the flow and applicable extensions.

At a high level:

```text
response_type
    ↓
What response does the Client request?

client_id
    ↓
Which Client is making the request?

redirect_uri
    ↓
Where should the response be returned?

scope
    ↓
What authorization is being requested?

state
    ↓
Which authorization transaction does this response belong to?

code_challenge
    ↓
What PKCE binding should be enforced later?
```

RFC 6749 defines the core authorization request parameters for the Authorization Code Grant.

---

# 6. `response_type`

For the Authorization Code flow:

```text
response_type=code
```

The value tells the Authorization Server that the Client is requesting an authorization code.

Conceptually:

```text
response_type
      ↓
     code
      ↓
Authorization Code response
```

This parameter describes the requested response type.

It does **not** mean:

```text
"I want an Access Token immediately."
```

Modern OAuth security guidance specifically recommends authorization-code-based flows instead of the historical Implicit Grant response type for modern deployments because access tokens returned directly in authorization responses create additional leakage and replay risks.

---

# 7. `client_id`

The `client_id` identifies the OAuth Client.

For example:

```text
client_id=client-123
```

Conceptually:

```text
client_id
    ↓
"Which registered Client is requesting authorization?"
```

The value is an identifier.

It should not automatically be treated as a credential or password.

The Authorization Server uses the identifier to locate the Client's registered configuration and apply the appropriate policy.

RFC 6749 defines `client_id` as a required authorization request parameter for the Authorization Code Grant.

---

# 8. `redirect_uri`

The `redirect_uri` tells the Authorization Server where the authorization response is to be sent.

For example:

```text
redirect_uri=https://client.example/callback
```

Conceptually:

```text
Authorization Server
        │
        │ Authorization Response
        ▼
https://client.example/callback
```

This parameter is security-critical because the authorization response can contain credentials such as an authorization code.

An attacker who can cause the response to be sent to an attacker-controlled destination may be able to obtain those credentials.

---

# 9. Redirect URI Must Be Controlled

The Client should not be able to invent an arbitrary destination such as:

```text
https://attacker.example/callback
```

when the Authorization Server expects:

```text
https://client.example/callback
```

The modern security rule is stricter than a vague hostname or prefix comparison.

RFC 9700 requires Authorization Servers to use **exact string matching** when comparing Client redirect URIs against pre-registered redirect URIs, with the documented localhost port exception for native applications.

Therefore:

```text
Registered:
https://client.example/callback

Requested:
https://client.example/callback
```

matches.

But:

```text
Registered:
https://client.example/callback

Requested:
https://client.example/callback/other
```

does not automatically match.

Likewise:

```text
https://client.example
```

and:

```text
https://client.example.evil.example
```

are different values.

---

# 10. Why Prefix Matching Is Dangerous

An insecure implementation might do:

```text
if requested_uri.startsWith(registered_uri)
```

This can create unintended valid destinations.

For example:

```text
Registered:
https://client.example/callback

Attacker:
https://client.example/callback.attacker.example
```

A weak comparison can accidentally treat the attacker-controlled value as valid.

The current security model instead requires exact matching for registered redirect URIs, subject to the specific native-app localhost exception.

The lesson is:

```text
Redirect URI validation
    =
Security boundary
```

not merely configuration validation.

---

# 11. `scope`

The `scope` parameter identifies the authorization scope requested by the Client.

For example:

```text
scope=files.read files.write
```

Conceptually:

```text
Client
   │
   │ Requested Scope
   ▼
Authorization Server
   │
   │ Authorization Decision
   ▼
Granted Scope
```

The Client must not assume:

```text
Requested Scope
    =
Granted Scope
```

The Authorization Server ultimately determines what authorization is granted according to its policy and the Resource Owner's authorization.

RFC 6749 defines `scope` as the scope of the access request.

---

# 12. Requested Scope Is a Request, Not a Privilege Escalation

Suppose the Client asks for:

```text
scope=read write admin
```

That does not mean the Client automatically receives all three permissions.

The Authorization Server may grant:

```text
read
write
```

and deny:

```text
admin
```

Conceptually:

```text
Requested
   │
   ├── read
   ├── write
   └── admin
          │
          ▼
Authorization Decision
          │
          ▼
Granted
   ├── read
   └── write
```

The requested scope therefore participates in the authorization decision rather than bypassing it.

---

# 13. `state`

The `state` parameter allows the Client to maintain state between the Authorization Request and the eventual authorization response.

For example:

```text
Authorization Request

state=ABC123
```

and later:

```text
Authorization Response

state=ABC123
```

Conceptually:

```text
Client
  │
  │ state = ABC123
  ▼
Authorization Server
  │
  │ state = ABC123
  ▼
Client
```

The Client uses the value to associate the incoming response with the authorization transaction it previously initiated.

RFC 6749 defines `state` as a recommended opaque value for maintaining state between the request and callback.

---

# 14. `state` and CSRF Protection

`state` is not merely a convenience for remembering application state.

It can provide an important CSRF defense when used correctly.

The security model is:

```text
Client creates transaction
        │
        │ random state
        ▼
Authorization Server
        │
        │ response + state
        ▼
Client
        │
        │ compare against pending transaction
        ▼
Accept / Reject
```

A forged authorization response that does not correspond to a pending transaction can then be rejected.

RFC 9700 states that Clients must prevent CSRF and describes securely bound one-time values carried in `state` as one mechanism for doing so when PKCE or an applicable OIDC mechanism is not being relied upon.

The critical requirement is not simply:

```text
state exists
```

but:

```text
state is unpredictable
+
state is transaction-specific
+
state is securely bound to the authorization transaction
```

---

# 15. PKCE Begins in the Authorization Request

PKCE introduces an additional security binding between the authorization request and the later token request.

The Client creates:

```text
code_verifier
```

and derives:

```text
code_challenge
```

It sends the challenge in the Authorization Request:

```text
Authorization Request
    │
    └── code_challenge
```

Later, during token exchange:

```text
Token Request
    │
    └── code_verifier
```

The Authorization Server can verify that the same Client that initiated the transaction possesses the verifier.

RFC 7636 defines this mechanism, and RFC 9700 now requires Authorization Servers to support PKCE and requires public Clients to use it.

---

# 16. `code_challenge_method=S256`

For modern PKCE deployments, the Client should use:

```text
code_challenge_method=S256
```

Conceptually:

```text
code_verifier
      │
      │ SHA-256
      ▼
code_challenge
```

The Client sends:

```text
code_challenge_method=S256
```

and:

```text
code_challenge=...
```

in the Authorization Request.

RFC 9700 identifies `S256` as the currently appropriate PKCE challenge method because it does not expose the verifier in the authorization request.

---

# 17. Transaction Binding

At this point, the Authorization Request is no longer just a collection of parameters.

It establishes a transaction context.

Conceptually:

```text
Authorization Transaction
        │
        ├── client_id
        ├── redirect_uri
        ├── scope
        ├── state
        └── code_challenge
```

These values become important during later protocol processing.

The Client should therefore preserve the relevant transaction state securely until the authorization response is processed.

---

# 18. Building the Request

A production-oriented Client should construct the Authorization Request from trusted configuration and newly generated transaction data.

Conceptually:

```text
Trusted Client Configuration
        │
        ├── client_id
        ├── authorization_endpoint
        └── registered redirect_uri
        │
        ▼
New Authorization Transaction
        │
        ├── state
        ├── code_verifier
        └── code_challenge
        │
        ▼
Authorization Request
```

This is different from allowing arbitrary request parameters to flow directly from untrusted application input.

---

# 19. The User Agent Carries the Request

Once the Client has constructed the request, it directs the user's user agent to the Authorization Endpoint.

```text
Client
  │
  │ Redirect / navigation
  ▼
User Agent
  │
  │ Authorization Request
  ▼
Authorization Server
```

The Browser therefore transports the request and displays the Authorization Server's interaction to the Resource Owner.

The Client itself does not have to collect the Resource Owner's Authorization Server password.

This separation is particularly important for modern application architectures.

---

# 20. Authorization Request and HTTPS

Authorization requests and responses carry security-sensitive information.

RFC 6749's security model relies on TLS for communication involving the authorization protocol, and current OAuth security guidance requires authorization responses to be protected from unencrypted transport.

For ordinary web deployments, the practical baseline is:

```text
Authorization Endpoint
        ↓
HTTPS

Redirect URI
        ↓
HTTPS
```

The specific localhost exception for native applications is defined separately by RFC 8252.

---

# 21. Modern Mix-Up Protection

A Client can interact with more than one Authorization Server.

For example:

```text
Client
 ├── Authorization Server A
 └── Authorization Server B
```

If the Client cannot reliably identify which server produced an authorization response, it may send a credential such as an authorization code to the wrong server.

This is the basis of an OAuth mix-up attack.

RFC 9207 defines an authorization-response parameter:

```text
iss
```

that explicitly identifies the Authorization Server.

When supported, the Client compares the returned issuer with the expected issuer and rejects the response when they differ.

RFC 9700 identifies issuer-based mix-up defense as a required consideration for Clients interacting with multiple Authorization Servers.

---

# 22. The Authorization Request Does Not Contain Trust by Itself

A subtle but important point:

```text
client_id
redirect_uri
scope
state
code_challenge
```

are values in a protocol request.

Their presence does not make them trustworthy merely because they are inside a URL.

The Client must construct security-sensitive values correctly.

The Authorization Server must validate the request.

The Client must later validate the authorization response.

Therefore:

```text
Request parameter
    ≠
Trusted value
```

---

# 23. What the Authorization Server Does

When the Authorization Server receives the request, it evaluates it.

Conceptually:

```text
Authorization Request
        │
        ▼
┌───────────────────────────┐
│ Authorization Server      │
│                           │
│ Identify Client           │
│ Validate redirect URI     │
│ Validate request          │
│ Process authorization     │
│ Apply policy              │
└─────────────┬─────────────┘
              │
              ▼
       Continue / Reject
```

The exact sequence depends on the authorization server and protocol profile.

But the important principle is:

```text
Client requests
        ↓
Authorization Server decides
```

---

# 24. Redirect URI and Client Registration

The relationship between registration and request is:

```text
Client Registration
        │
        └── Approved redirect URI
                    │
                    ▼
Authorization Request
                    │
                    └── redirect_uri
```

The requested URI must comply with the Authorization Server's registered Client configuration.

Current OAuth security guidance requires exact matching for redirect URIs, rather than loose matching rules.

This is one of the clearest examples of why Client registration is part of the security model rather than just administrative setup.

---

# 25. Authorization Request as a Security Contract

The request can be viewed as a contract between the Client and Authorization Server:

```text
Client
  │
  │ "I am Client X."
  │
  │ "I want this authorization."
  │
  │ "Return the response here."
  │
  │ "Bind this transaction to this PKCE challenge."
  ▼
Authorization Server
```

The Authorization Server then decides whether the request is valid and whether the Resource Owner grants the requested authorization.

The resulting transaction continues into the authorization response.

---

# 26. What We Are Not Covering Yet

This lecture intentionally does not go deeply into:

```text
Authorization Code redemption
Token Endpoint
Access Token response
Refresh Token
ID Token
Resource Server validation
```

Those are separate protocol stages.

The current focus is:

```text
How does the Client initiate
an authorization transaction correctly?
```

That boundary keeps the learning model clear:

```text
Authorization Request
        ↓
Authorization Response
        ↓
Authorization Code
        ↓
Token Exchange
```

Only the first stage is the focus here.

---

# 27. Production Implementation Checklist

Before sending an Authorization Request, a production Client should be able to answer:

```text
[ ] Do I know the intended Authorization Server?

[ ] Do I know the correct Authorization Endpoint?

[ ] Is my client_id from trusted Client configuration?

[ ] Is my redirect_uri registered and exact?

[ ] Am I requesting only the scopes I actually need?

[ ] Have I generated a transaction-specific state value
    when state is needed for the deployment?

[ ] Am I using PKCE where required?

[ ] Is the PKCE challenge transaction-specific?

[ ] Am I using S256 for PKCE?

[ ] Am I preserving the transaction context securely?

[ ] If multiple Authorization Servers are supported,
    do I have a mix-up defense?

[ ] Is the authorization interaction protected by HTTPS?
```

Current OAuth Security BCP establishes exact redirect URI matching, CSRF protection, PKCE requirements, mix-up defenses, and modern authorization-code protections as important parts of a secure OAuth deployment.

---

# 28. Practical Mental Model

Think of the Authorization Request as:

```text
            START A TRANSACTION

Client
  │
  │ Who am I?
  │       → client_id
  │
  │ What do I want?
  │       → scope
  │
  │ What response do I want?
  │       → response_type
  │
  │ Where should the response return?
  │       → redirect_uri
  │
  │ Which transaction is this?
  │       → state
  │
  │ How will the authorization code be bound?
  │       → code_challenge
  │
  ▼
Authorization Server
```

The Authorization Request therefore establishes the **identity, destination, requested authorization, and security context** for the authorization transaction.

---

# 29. Knowledge Check

### Question 1

What is an OAuth Authorization Request?

### Question 2

What is the purpose of the Authorization Endpoint?

### Question 3

What does `response_type=code` request?

### Question 4

What does `client_id` identify?

### Question 5

Why is `redirect_uri` security-critical?

### Question 6

Why is exact redirect URI matching important?

### Question 7

Does requesting a scope guarantee that the scope will be granted?

### Question 8

What problem does `state` help address?

### Question 9

Where does PKCE enter the Authorization Request?

### Question 10

Why is `S256` the preferred PKCE challenge method?

### Question 11

Why does issuer identification matter when a Client supports multiple Authorization Servers?

### Question 12

Why should an Authorization Request be treated as the beginning of a security-sensitive transaction rather than just a URL?

---

# 30. Lecture Summary

An OAuth Authorization Request is the mechanism by which a Client initiates an authorization transaction with an Authorization Server through the user's user agent.

A typical Authorization Code request contains concepts such as:

```text
response_type
client_id
redirect_uri
scope
state
code_challenge
code_challenge_method
```

Their roles are fundamentally different:

```text
response_type
    ↓
Requested response

client_id
    ↓
Client identity

redirect_uri
    ↓
Response destination

scope
    ↓
Requested authorization

state
    ↓
Transaction correlation / CSRF defense

code_challenge
    ↓
PKCE transaction binding
```

The most important security properties are:

```text
Exact Redirect URI Matching
Transaction-Specific State
PKCE
S256
HTTPS
Issuer-Based Mix-Up Defense
```

The modern mental model is:

```text
Trusted Client Configuration
        +
Transaction-Specific Security Data
        ↓
Authorization Request
        ↓
Authorization Server Validation
        ↓
Resource Owner Authorization
        ↓
Authorization Response
```

The key distinction to retain is:

```text
Authorization Request
    =
"I want to start an authorization transaction."

Authorization Decision
    =
"The Authorization Server / Resource Owner
decided what authorization is granted."
```

---

# 31. References

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Primary source for:
- Authorization Endpoint
- Authorization Request
- response_type
- client_id
- redirect_uri
- scope
- state
- Authorization Code Grant


RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Current general OAuth security guidance.

Relevant to this lecture:
- Exact redirect URI matching
- CSRF protection
- PKCE
- Authorization-code protection
- Mix-up attack defense
- HTTPS
- Modern Authorization Code guidance


RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html

Defines PKCE:
- code_verifier
- code_challenge
- code_challenge_method


RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification
https://www.rfc-editor.org/rfc/rfc9207.html

Defines the authorization-response `iss` parameter
and its use for Authorization Server identification
and mix-up attack mitigation.


RFC 8252 — OAuth 2.0 for Native Apps
https://www.rfc-editor.org/rfc/rfc8252.html

Relevant to native-app authorization requests,
external user-agents, redirect URI handling,
and public-client PKCE requirements.


RFC 8414 — OAuth 2.0 Authorization Server Metadata
https://www.rfc-editor.org/rfc/rfc8414.html

Relevant to obtaining Authorization Server configuration,
including the Authorization Endpoint and PKCE capabilities.


RFC 10017 — OAuth 2.0 for Browser-Based Applications
https://www.rfc-editor.org/rfc/rfc10017.html

Current browser-based OAuth guidance.

Relevant to:
- Browser-based Clients
- Exact redirect URI usage
- Browser-specific threats
- Modern Authorization Code + PKCE deployment
```

---

# 32. Source Update Analysis

The foundational Authorization Request model comes from RFC 6749.

Its current interpretation is not based on RFC 6749 alone.

```text
RFC 6749
    ↓
Defines the core Authorization Request
    │
    ├── response_type
    ├── client_id
    ├── redirect_uri
    ├── scope
    └── state

RFC 7636
    ↓
Adds PKCE
    │
    ├── code_challenge
    └── code_challenge_method

RFC 9207
    ↓
Adds explicit authorization-server
issuer identification in responses

RFC 9700
    ↓
Strengthens current security requirements
    │
    ├── Exact redirect URI matching
    ├── CSRF protection
    ├── PKCE
    ├── Mix-up defenses
    ├── Authorization-code protection
    └── Secure transport

RFC 8252
    ↓
Specializes authorization-request handling
for native applications

RFC 10017
    ↓
Adds current browser-specific guidance
for browser-based Clients
```

These updates affect the lecture itself.

Therefore the Authorization Request is taught here as:

```text
RFC 6749 Foundation
        +
PKCE
        +
Current OAuth Security BCP
        +
Deployment-specific guidance
        ↓
Modern Authorization Request
```

rather than as the historical RFC 6749 request format alone.
