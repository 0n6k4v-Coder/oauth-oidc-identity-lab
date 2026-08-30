# Lecture 07 — OAuth 2.0 Refresh Token

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Long-Lived Authorization & Token Lifecycle
> **Prerequisite:** Understanding of Authorization Code, Token Exchange, and Access Token basics

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what a Refresh Token is and why OAuth uses it.
* Distinguish a Refresh Token from an Access Token.
* Explain when a Client uses a Refresh Token.
* Understand the Refresh Token Grant at the Token Endpoint.
* Understand the relationship between a Refresh Token and the Client to which it was issued.
* Explain why Refresh Tokens require stronger protection than short-lived Access Tokens.
* Understand Refresh Token scope and resource restrictions.
* Explain Refresh Token rotation.
* Explain Refresh Token replay detection.
* Explain sender-constrained Refresh Tokens.
* Understand the security trade-offs between rotation and sender-constraining.
* Explain Refresh Token expiration and inactivity-based expiration.
* Understand Refresh Token revocation.
* Recognize what happens when a Refresh Token is compromised.
* Understand why browser-based Clients require special Refresh Token security considerations.
* Apply the current OAuth Security Best Current Practice to Refresh Token handling.

---

# 2. Why Does OAuth Need Refresh Tokens?

Access Tokens are commonly issued with a limited lifetime.

For example:

```text
Access Token
    ↓
Valid for a limited period
    ↓
Expires
```

Suppose the user has authorized a Client for a long-running session.

Without a Refresh Token, the Client may need to send the user through the authorization process again whenever the Access Token expires.

That creates unnecessary authorization interaction.

A Refresh Token provides another mechanism:

```text
Access Token expires
        ↓
Client uses Refresh Token
        ↓
Token Endpoint
        ↓
New Access Token
```

The important idea is:

```text
Refresh Token
    =
Credential used to obtain new Access Tokens
```

It is not normally presented directly to the Resource Server.

RFC 6749 defines the Refresh Token as a credential used by the Client to obtain a new Access Token when the current Access Token becomes invalid or expires. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 3. Access Token vs Refresh Token

These tokens serve different purposes.

```text
Access Token
    ↓
Access protected resources

Refresh Token
    ↓
Obtain new Access Tokens
```

Conceptually:

```text
                 Authorization Server
                        │
                        │
                 Token Response
                        │
               ┌────────┴────────┐
               │                 │
               ▼                 ▼
         Access Token       Refresh Token
               │                 │
               │                 │
               ▼                 ▼
        Resource Server     Token Endpoint
```

Therefore:

```text
Access Token
    ≠
Refresh Token
```

The Access Token is intended for the Resource Server.

The Refresh Token is intended for the Authorization Server.

---

# 4. Why Not Use the Access Token Forever?

A long-lived Access Token increases the impact of token leakage.

Consider:

```text
Access Token
    ↓
Stolen by attacker
    ↓
Attacker can use it
    ↓
Until token expires or is otherwise invalidated
```

Shorter Access Token lifetimes reduce this exposure window.

But short-lived Access Tokens create another problem:

```text
Access Token
    ↓
Expires frequently
    ↓
User must authorize again
```

Refresh Tokens provide a mechanism for maintaining authorization without repeatedly requiring the full authorization interaction.

The security architecture therefore often becomes:

```text
Short-lived Access Token
        +
Longer-lived Refresh Token
        ↓
Usability + reduced Access Token exposure
```

RFC 6749 and RFC 9700 both treat Refresh Tokens as long-lived credentials requiring particular security protections. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 5. Where the Refresh Token Fits

The complete lifecycle can be represented as:

```text
Authorization
      ↓
Authorization Code
      ↓
Token Exchange
      ↓
Access Token + Refresh Token
      │             │
      │             │
      ▼             ▼
Resource Server   Token Endpoint
      │             │
      │             │ Refresh
      │             ▼
      │        New Access Token
      │
      ▼
Protected Resource
```

The Refresh Token therefore creates a second interaction with the Token Endpoint after the initial Authorization Code exchange.

---

# 6. Who Issues the Refresh Token?

The Authorization Server decides whether to issue a Refresh Token.

It is not automatically required to issue one.

Conceptually:

```text
Client
   │
   │ Authorization Code
   ▼
Token Endpoint
   │
   ▼
Authorization Server
   │
   ├── Access Token
   │
   └── Refresh Token
```

RFC 6749 allows Authorization Servers to issue Refresh Tokens.

Current OAuth Security BCP goes further and says Authorization Servers must determine, based on risk assessment, whether issuing a Refresh Token to a particular Client is appropriate. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

Therefore:

```text
Refresh Token
    ≠
Always issued
```

---

# 7. The Refresh Token Grant

Once the Client has a Refresh Token, it can request a new Access Token using the:

```text
refresh_token
```

grant type.

The request is sent to the Token Endpoint.

Conceptually:

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=REFRESH_TOKEN
```

RFC 6749 defines:

```text
grant_type=refresh_token
```

and requires:

```text
refresh_token
```

in the request.

([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 8. Refresh Token Flow

The basic flow is:

```text
Client
   │
   │ Refresh Token
   ▼
Token Endpoint
   │
   │ Validate
   ▼
Authorization Server
   │
   │ New Access Token
   ▼
Client
```

A more complete model is:

```text
Access Token expires
        ↓
Client detects expiration
        ↓
Client sends Refresh Token
        ↓
Token Endpoint
        ↓
Authorization Server validates
        ↓
New Access Token
        ↓
Client
```

The Client does not send the Refresh Token to the Resource Server.

---

# 9. The Refresh Token Request

A simplified request is:

```http
POST /token HTTP/1.1
Host: authorization.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=REFRESH_TOKEN
```

Depending on the Client type and authorization-server configuration, the request may additionally contain:

```text
client_id
client authentication
scope
resource
DPoP proof
```

The exact parameters depend on the deployment and applicable specifications.

---

# 10. Client Binding

A Refresh Token is associated with the Client to which it was issued.

Conceptually:

```text
Client A
    │
    │
    ▼
Refresh Token A
```

This does not mean:

```text
Client B
    │
    │ Refresh Token A
    ▼
Authorization Server
    ↓
Accept
```

The Authorization Server must maintain the binding between the Refresh Token and the Client.

RFC 6749 requires the Authorization Server to maintain this binding and verify it whenever the Client identity can be authenticated. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 11. Confidential Clients

For a confidential Client, the Authorization Server can authenticate the Client when the Refresh Token is presented.

Conceptually:

```text
Client
   │
   ├── Refresh Token
   │
   └── Client Authentication
   │
   ▼
Token Endpoint
```

The server can then establish:

```text
This Refresh Token
        +
This authenticated Client
        ↓
Expected binding
```

RFC 6749 requires confidential Clients to authenticate when using the Token Endpoint, including when using a Refresh Token. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 12. Public Clients

A public Client cannot safely rely on a static Client Secret.

For example:

```text
Browser Application
    ↓
Client Secret
    ↓
JavaScript bundle
    ↓
User can inspect it
```

Therefore:

```text
client_secret
    ≠
Reliable protection for a browser Client
```

This is important because Refresh Tokens can be long-lived and therefore have a larger security impact than many short-lived credentials.

Current OAuth Security BCP requires public clients that receive Refresh Tokens to use either:

```text
Sender-Constrained Refresh Tokens
```

or:

```text
Refresh Token Rotation
```

to detect replay. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 13. Refresh Token Scope

A Refresh Token should not silently create broader authorization than the original authorization grant.

RFC 9700 requires issued Refresh Tokens to be bound to the scope and resource servers consented to by the Resource Owner.

Conceptually:

```text
Original Authorization
        │
        ├── Scope
        └── Resource Servers
        │
        ▼
Refresh Token
```

The Refresh Token should remain within that authorization boundary.

Therefore:

```text
Refresh Token
    ≠
Unlimited permission to request anything
```

This protects against privilege escalation and reduces the impact of Refresh Token leakage.

([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 14. Can the Client Increase Scope During Refresh?

RFC 6749 allows the Client to request a scope during Refresh Token use.

However:

```text
Requested Scope
    ⊆
Originally Granted Scope
```

A Client cannot use a Refresh Token to request arbitrary additional permissions that were never granted.

Conceptually:

```text
Originally Granted:
read profile
read calendar

Refresh Request:
read profile
```

Valid.

But:

```text
Originally Granted:
read profile

Refresh Request:
read profile
write payments
```

cannot be accepted merely because the Client possesses the Refresh Token.

RFC 6749 requires the requested scope to not include privileges beyond the scope originally granted. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6749.html))

---

# 15. Why Refresh Tokens Are High-Value Credentials

A short-lived Access Token may provide access for:

```text
10 minutes
```

while a Refresh Token may remain useful for substantially longer.

Therefore:

```text
Refresh Token
      ↓
Can repeatedly obtain
new Access Tokens
      ↓
Potentially extended compromise
```

This makes Refresh Token theft particularly serious.

RFC 10017 explicitly notes that for browser-based applications, leaked Refresh Tokens can allow an attacker to continue obtaining new Access Tokens, potentially without detection. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 16. Refresh Token Rotation

One major defense is:

```text
Refresh Token Rotation
```

Instead of allowing one Refresh Token to remain reusable indefinitely:

```text
RT₁
 ↓
Refresh
 ↓
AT₁ + RT₂
```

The old token:

```text
RT₁
```

is invalidated.

The Client receives:

```text
RT₂
```

for the next refresh.

Then:

```text
RT₂
 ↓
Refresh
 ↓
AT₂ + RT₃
```

This creates a chain:

```text
RT₁ → RT₂ → RT₃ → RT₄
```

---

# 17. Why Rotation Helps

Suppose an attacker steals:

```text
RT₁
```

The legitimate Client later uses:

```text
RT₁
```

and receives:

```text
RT₂
```

with:

```text
RT₁
```

invalidated.

Now the attacker attempts:

```text
RT₁
   ↓
Token Endpoint
```

The server sees:

```text
RT₁ already invalidated
```

This indicates possible replay.

Conceptually:

```text
RT₁
 │
 ├── Legitimate Client → RT₂
 │
 └── Attacker → RT₁ again
                  ↓
              Replay detected
```

RFC 9700 describes this as a mechanism for detecting Refresh Token replay for public Clients. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 18. Refresh Token Family

A rotation implementation normally retains information about the relationship between successive Refresh Tokens.

Conceptually:

```text
Grant
 │
 └── Refresh Token Family
       │
       ├── RT₁
       ├── RT₂
       ├── RT₃
       └── RT₄
```

This allows the Authorization Server to recognize that a previously invalidated Refresh Token is being presented again.

The exact internal data model is implementation-specific.

The important security property is:

```text
Rotation
    +
Replay Detection
```

---

# 19. What Happens After Replay Detection?

A Refresh Token reuse event is security-sensitive.

For example:

```text
RT₁
 ↓
Used legitimately
 ↓
RT₁ invalidated
 ↓
RT₁ used again
 ↓
Possible compromise
```

The Authorization Server can treat this as evidence that the token family may have been compromised.

Depending on implementation policy, the server may invalidate related tokens or the underlying authorization grant.

RFC 9700 specifies replay detection requirements, while the precise containment policy depends on the authorization-server implementation and deployment risk model. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 20. Sender-Constrained Refresh Tokens

Another replay defense is sender-constraining.

The idea is:

```text
Refresh Token
      +
Proof of key possession
      ↓
Valid refresh request
```

The Refresh Token is cryptographically bound to a Client instance or key.

A stolen token alone is therefore insufficient.

Conceptually:

```text
Refresh Token
      +
Private Key
      ↓
Client
      ↓
Token Endpoint
```

An attacker who obtains only:

```text
Refresh Token
```

cannot satisfy the sender-constraint requirement.

RFC 9700 identifies sender-constrained Refresh Tokens as one of the two required replay-detection approaches for public Clients receiving Refresh Tokens. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 21. DPoP as a Sender-Constraint Mechanism

RFC 9449 defines:

```text
OAuth 2.0 Demonstrating Proof of Possession
```

or:

```text
DPoP
```

DPoP uses a public/private key pair.

Conceptually:

```text
Client
   │
   ├── Private Key
   │
   └── Public Key
```

The Authorization Server can bind a Refresh Token for a public Client to the public key.

When the Refresh Token is later used:

```text
Refresh Token
      +
DPoP Proof
      ↓
Token Endpoint
```

The server verifies that the proof demonstrates possession of the same key.

RFC 9449 explicitly defines sender-constraining Refresh Tokens issued to public Clients using DPoP. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9449.html))

---

# 22. Sender Constraint Does Not Mean "Impossible to Steal"

Sender-constraining changes the attack requirement.

Without sender constraint:

```text
Steal Refresh Token
        ↓
Potentially replay
```

With sender constraint:

```text
Steal Refresh Token
        ↓
Need associated key
        ↓
Without key
        ↓
Replay blocked
```

However:

```text
Refresh Token
      +
Associated Key
      ↓
Protection can be defeated
```

RFC 9700 explicitly notes that the security of sender-constrained tokens is undermined if an attacker obtains both the token and its key material, especially when client software is compromised or exposed to XSS. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

Therefore:

```text
Sender Constraint
    =
Replay resistance
    ≠
Absolute security
```

---

# 23. Rotation vs Sender Constraint

The two mechanisms address replay differently.

## Rotation

```text
RT₁
 ↓
RT₂
 ↓
RT₃
```

The old token becomes invalid.

The Authorization Server can detect reuse.

---

## Sender Constraint

```text
RT₁
 +
Key
 ↓
Valid request
```

The token is usable only with proof of possession of the associated key.

---

## Comparison

| Property | Rotation | Sender Constraint |
|---|---|---|
| Protects against token-only theft | Yes, through replay detection | Yes |
| Requires key management | No | Yes |
| Detects reuse of an old token | Yes | Not necessarily |
| Requires proof of possession | No | Yes |
| Works with public Clients | Yes | Yes |
| Can be defeated if token + key are compromised | Not in the same way | Yes |
| Operational complexity | Token family state | Cryptographic key lifecycle |

RFC 9700 defines both as valid replay-detection mechanisms for public Clients. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 24. Can Both Be Used?

Yes.

Rotation and sender-constraining are not conceptually mutually exclusive.

A deployment can use:

```text
Refresh Token Rotation
        +
Sender-Constrained Refresh Token
```

to create defense in depth.

For example:

```text
RT₁ + Key
   ↓
Refresh
   ↓
RT₂ + Key
   ↓
RT₁ invalidated
```

An attacker who steals only:

```text
RT₁
```

cannot satisfy the sender constraint.

An attacker who somehow possesses:

```text
RT₁ + Key
```

may still be detected if the old rotated token is subsequently replayed.

Whether both are appropriate depends on the security architecture and implementation capabilities.

RFC 9700 requires one of these mechanisms for public Clients receiving Refresh Tokens; using both can provide additional defense, but it is not a replacement for protecting the Client and its key material. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 25. Refresh Token Lifetime

A Refresh Token should not necessarily live forever.

Current OAuth security guidance requires Authorization Servers to consider Refresh Token expiration.

For browser-based applications, RFC 10017 goes further and requires Authorization Servers to either:

```text
Set a maximum Refresh Token lifetime
```

or:

```text
Expire the Refresh Token after a period of inactivity
```

This limits the amount of time a stolen Refresh Token can remain useful.

([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 26. Why Lifetime Matters

Suppose:

```text
Refresh Token lifetime = 30 days
```

and an attacker steals it.

The attacker may potentially continue obtaining new Access Tokens throughout that period unless another protection detects or blocks the misuse.

Therefore:

```text
Long lifetime
    ↓
Large compromise window
```

while:

```text
Limited lifetime
    ↓
Smaller compromise window
```

Refresh Token lifetime should therefore be determined according to the application's security risk rather than convenience alone.

---

# 27. Inactivity Expiration

An alternative to a fixed absolute lifetime is expiration based on inactivity.

Conceptually:

```text
Refresh Token
      ↓
Used regularly
      ↓
Remains active
```

but:

```text
Refresh Token
      ↓
Unused for configured period
      ↓
Expires
```

This can support long-running active sessions while limiting abandoned credentials.

Current browser-based OAuth guidance explicitly allows this form of expiration. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 28. Rotation and Overall Lifetime

There is an important subtlety with rotation.

Suppose:

```text
Initial Refresh Token
lifetime = 8 hours
```

and the Client repeatedly refreshes:

```text
RT₁ → RT₂ → RT₃ → RT₄
```

The server should not blindly turn rotation into an unlimited lifetime.

For browser-based applications, RFC 10017 requires that when an initial Refresh Token has a pre-established expiration time, rotated Refresh Tokens must not extend the lifetime beyond the initial token's lifetime.

Conceptually:

```text
Initial lifetime
│
├── RT₁
├──── RT₂
├────── RT₃
└──────── RT₄
       │
       ▼
Initial expiration boundary
```

This prevents a stolen Refresh Token from remaining continuously renewable forever through rotation. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 29. Refresh Token Revocation

A Refresh Token may also be explicitly revoked.

OAuth defines a dedicated Token Revocation specification:

```text
RFC 7009
OAuth 2.0 Token Revocation
```

A Client can send:

```http
POST /revoke
Content-Type: application/x-www-form-urlencoded

token=REFRESH_TOKEN&
token_type_hint=refresh_token
```

The Authorization Server invalidates the token.

RFC 7009 defines Refresh Token revocation and permits authorization-server policies that also invalidate related tokens or the underlying authorization grant. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc7009.html))

---

# 30. When Should Refresh Tokens Be Revoked?

Possible scenarios include:

```text
User logs out
Application is uninstalled
Authorization is withdrawn
Security incident
Detected token replay
Account compromise
Client compromise
Administrative revocation
```

Conceptually:

```text
Security Event
      ↓
Authorization Server
      ↓
Revoke Refresh Token
      ↓
Future refresh request
      ↓
Rejected
```

Revocation is therefore an important containment mechanism.

---

# 31. Refresh Token Revocation vs Expiration

These are different mechanisms.

### Expiration

```text
Time / inactivity
      ↓
Token becomes invalid
```

### Revocation

```text
Security / administrative event
      ↓
Server explicitly invalidates token
```

Therefore:

```text
Expiration
    =
Automatic lifecycle boundary

Revocation
    =
Explicit invalidation
```

A robust deployment may use both.

---

# 32. Refresh Token Theft

Consider:

```text
Client
   │
   └── Refresh Token
          ↓
       Stolen
          ↓
       Attacker
```

The correct security response depends on the protection model.

### With rotation

```text
Attacker uses old token
        ↓
Replay detection
```

### With sender constraint

```text
Attacker has token
        ↓
No valid key proof
        ↓
Reject
```

### With both

```text
Token
 +
Key
 +
Rotation
        ↓
Multiple security barriers
```

However, if the attacker compromises the Client environment itself, the security problem becomes substantially larger.

---

# 33. Compromised Client

Suppose an attacker controls the Client execution environment.

They may obtain:

```text
Refresh Token
Private Key
Application State
```

At that point:

```text
Sender Constraint
    ↓
May no longer be sufficient
```

and:

```text
Rotation
    ↓
May detect replay
    but cannot prevent
    an already-compromised
    Client from acting legitimately
```

This is a critical distinction:

```text
Token theft
    ≠
Client compromise
```

Token protections reduce the impact of stolen credentials.

They do not guarantee safety after complete compromise of the Client environment.

---

# 34. Browser-Based Applications

Browser-based applications require special consideration.

A typical browser architecture is:

```text
Browser
   ↓
JavaScript Application
   ↓
Authorization Server
```

The browser environment may be exposed to:

```text
XSS
Malicious extensions
Compromised dependencies
Browser storage attacks
Malicious JavaScript
```

RFC 10017 therefore provides dedicated current guidance for browser-based OAuth applications.

If Refresh Tokens are issued to browser-based applications, the application and Authorization Server must follow the Refresh Token requirements in RFC 9700. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 35. Browser Refresh Token Risk

RFC 10017 explicitly highlights that Refresh Tokens in browser-based applications are often bearer credentials unless DPoP is used.

Therefore:

```text
Browser
   ↓
Refresh Token
   ↓
Token leakage
   ↓
Attacker may obtain new Access Tokens
```

This can be more damaging than a single leaked Access Token because the attacker may repeatedly obtain new tokens.

That is why browser-based applications require deliberate Refresh Token lifecycle and replay protection. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 36. Refresh Token Storage

A Refresh Token must be treated as highly sensitive.

At minimum:

```text
Do not log it.
Do not expose it unnecessarily.
Do not send it to the Resource Server.
Protect it in transit.
Protect it in storage.
```

For browser applications, token storage architecture becomes particularly important because JavaScript-accessible storage can be exposed if the application's execution environment is compromised.

The appropriate architecture depends on the browser application's design, including whether a Backend for Frontend or another server-side token-handling architecture is used.

RFC 10017 discusses these architectural choices and their security trade-offs. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 37. Refresh Token Error Handling

A Refresh Token request can fail.

Examples include:

```text
invalid_grant
invalid_client
invalid_request
unauthorized_client
```

A common condition is:

```text
invalid_grant
```

when the Refresh Token is:

```text
Invalid
Expired
Revoked
Not valid for this Client
```

The Client must not interpret a failed Refresh Token request as authorization success.

---

# 38. What Happens When Refresh Fails?

Suppose:

```text
Access Token
    ↓
Expired
```

The Client attempts:

```text
Refresh Token
    ↓
Token Endpoint
    ↓
invalid_grant
```

The Client may need to:

```text
Discard invalid credentials
        ↓
Require a new authorization flow
```

The exact user experience depends on the application.

The important protocol principle is:

```text
Refresh failure
    =
Do not continue pretending
the authorization is valid
```

---

# 39. Refresh Token Lifecycle

A complete lifecycle can be represented as:

```text
Authorization
      ↓
Initial Token Response
      │
      ├── Access Token
      └── Refresh Token
                 │
                 ▼
          Store securely
                 │
                 ▼
       Access Token expires
                 │
                 ▼
       Refresh Token Request
                 │
                 ▼
         Token Endpoint
                 │
          ┌──────┴──────┐
          │             │
       Valid          Invalid
          │             │
          ▼             ▼
    New Tokens        Error
          │
          ▼
   Rotate / Continue
          │
          ▼
   Refresh Token lifecycle
          │
     ┌────┴────┐
     │         │
 Expiration  Revocation
     │         │
     └────┬────┘
          ▼
       Invalid
```

---

# 40. Security Mental Model

A useful Refresh Token model is:

```text
             Refresh Token

                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
    Client       Lifetime     Scope /
    Binding                    Resource
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
             Replay Protection
                    │
             ┌──────┴──────┐
             │             │
          Rotation    Sender Constraint
             │             │
             └──────┬──────┘
                    ▼
               Revocation
                    │
                    ▼
              Secure Lifecycle
```

No single control is sufficient for every threat.

---

# 41. Modern Refresh Token Security Baseline

For a modern implementation, the conceptual baseline is:

```text
Risk Assessment
       ↓
Should a Refresh Token be issued?
       ↓
If issued:
       │
       ├── Bind to Client
       ├── Bind to authorized scope
       ├── Bind to authorized resources
       ├── Protect in transit
       ├── Protect in storage
       ├── Limit lifetime / inactivity
       └── Protect against replay
                  │
             Public Client
                  │
          ┌───────┴────────┐
          │                │
       Rotation     Sender Constraint
```

For public Clients, RFC 9700 requires one of the two replay-detection approaches above. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 42. What the Client Must Never Assume

Do not assume:

```text
Refresh Token
    =
Permanent login
```

Do not assume:

```text
Refresh Token
    =
Access Token
```

Do not assume:

```text
Possessing a Refresh Token
    =
Unlimited authorization
```

Do not assume:

```text
Rotation
    =
Token can never be stolen
```

Do not assume:

```text
Sender Constraint
    =
100% protection
```

Do not assume:

```text
Refresh Token
    =
Safe to log
```

Do not assume:

```text
Browser
    =
Safe place for a static client secret
```

---

# 43. Practical Design Example

Consider a public browser Client.

A modern design could be:

```text
Browser Client
      │
      │ Authorization Code + PKCE
      ▼
Authorization Server
      │
      │ Access Token
      │ Refresh Token
      ▼
Browser Client
```

For Refresh Token protection:

```text
Refresh Token Rotation
          +
limited lifetime
          +
scope/resource binding
          +
secure storage strategy
```

A deployment with DPoP may additionally use:

```text
Refresh Token
      +
DPoP key
```

The exact architecture should be selected based on the threat model and deployment design.

---

# 44. Production Checklist

Before issuing or accepting Refresh Tokens, verify:

```text
[ ] Have we decided whether this Client should receive a Refresh Token?

[ ] Is the Refresh Token bound to the correct Client?

[ ] Is the Refresh Token limited to the authorized scope?

[ ] Is the Refresh Token limited to the authorized resources?

[ ] Is the Refresh Token transmitted only over TLS?

[ ] Is the Refresh Token protected in storage?

[ ] Is the Refresh Token excluded from application logs?

[ ] Does the Client type require authentication?

[ ] If the Client is public, is replay protection implemented?

[ ] Is Refresh Token rotation implemented?

[ ] Or is sender-constraining implemented?

[ ] Would using both mechanisms materially improve this deployment?

[ ] Is Refresh Token lifetime limited?

[ ] Is inactivity expiration considered?

[ ] Is revocation supported?

[ ] Can replay be detected and contained?

[ ] Does the Client correctly handle refresh failure?

[ ] Does the architecture account for Client compromise?
```

---

# 45. Knowledge Check

### Question 1

What problem does a Refresh Token solve?

### Question 2

Why is a Refresh Token sent to the Token Endpoint rather than the Resource Server?

### Question 3

What is the difference between an Access Token and a Refresh Token?

### Question 4

Why is a Refresh Token generally considered a high-value credential?

### Question 5

Why must a Refresh Token be bound to the Client to which it was issued?

### Question 6

Why is a static Client Secret not sufficient for a browser-based public Client?

### Question 7

Why should a Refresh Token not be able to increase the privileges originally granted to the Client?

### Question 8

What is Refresh Token Rotation?

### Question 9

How can rotation detect Refresh Token replay?

### Question 10

What is a Refresh Token family?

### Question 11

What is a sender-constrained Refresh Token?

### Question 12

How can DPoP sender-constrain a Refresh Token?

### Question 13

Why does sender-constraining not provide absolute security?

### Question 14

What happens if an attacker obtains both the Refresh Token and its associated private key?

### Question 15

Can Refresh Token Rotation and Sender Constraint be used together?

### Question 16

Why should Refresh Tokens have a limited lifetime or inactivity expiration?

### Question 17

What is the difference between Refresh Token expiration and revocation?

### Question 18

Why are Refresh Tokens particularly sensitive in browser-based applications?

### Question 19

What should happen when a Refresh Token has been revoked or replayed?

### Question 20

Explain the complete Refresh Token lifecycle from initial issuance through expiration or revocation.

---

# 46. Lecture Summary

A Refresh Token is a credential used by a Client to obtain new Access Tokens from the Authorization Server.

The basic flow is:

```text
Access Token expires
        ↓
Client
        ↓
Refresh Token Request
        ↓
Token Endpoint
        ↓
Validation
        ↓
New Access Token
```

Refresh Tokens are not normally sent to Resource Servers.

They are bound to the Client and should remain within the scope and resource authorization granted by the Resource Owner.

The major security concern is that Refresh Tokens can be long-lived and can repeatedly produce new Access Tokens.

Therefore modern OAuth implementations must consider:

```text
Client Binding
Scope / Resource Binding
Secure Storage
TLS
Limited Lifetime
Inactivity Expiration
Revocation
Replay Detection
```

For public Clients, current OAuth Security BCP requires replay detection through either:

```text
Refresh Token Rotation
```

or:

```text
Sender-Constrained Refresh Tokens
```

Sender-constraining can use mechanisms such as DPoP.

Rotation provides replay detection by invalidating the previous Refresh Token when a new one is issued.

These mechanisms can also be combined for defense in depth.

However:

```text
Token Security
    ≠
Absolute Security
```

If an attacker compromises the Client environment and obtains both the Refresh Token and associated key material, sender-constraining may no longer provide protection.

The central mental model is:

```text
                 Refresh Token
                       │
                       ▼
              Token Endpoint
                       │
              Security Validation
                       │
             ┌─────────┴─────────┐
             │                   │
          Rotation          Sender Constraint
             │                   │
             └─────────┬─────────┘
                       ▼
                 Replay Defense
                       │
                       ▼
                New Access Token
```

The most important distinction is:

```text
Access Token
    =
Access protected resource

Refresh Token
    =
Obtain new Access Tokens
```

A Refresh Token is therefore not a longer-lived Access Token.

It is a separate credential with a different purpose and a different security lifecycle.

---

# 47. References

## 47.1 RFC 6749 — The OAuth 2.0 Authorization Framework

**Authority:** Internet Engineering Task Force (IETF)

**Role:** Foundational OAuth 2.0 specification.

Official source:

https://www.rfc-editor.org/rfc/rfc6749.html

Relevant sections:

```text
Section 1.5
Refresh Token

Section 3.2
Token Endpoint

Section 4.1
Authorization Code Grant

Section 6
Refreshing an Access Token

Section 10.4
Refresh Tokens
```

RFC 6749 defines the Refresh Token, the `refresh_token` grant type, Client binding, scope restrictions, TLS requirements, and basic refresh behavior.

---

## 47.2 RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 240).

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

Relevant topic:

```text
Section 4.14
Refresh Token Protection
```

This is the primary modern security source for this lecture.

It introduces or clarifies requirements including:

```text
Risk-based Refresh Token issuance
Scope and resource binding
Refresh Token replay protection
Sender-constrained Refresh Tokens
Refresh Token rotation
Public Client requirements
Token leakage mitigation
```

For public Clients, it requires Authorization Servers to use either sender-constrained Refresh Tokens or Refresh Token rotation to detect replay.

---

## 47.3 RFC 9449 — OAuth 2.0 Demonstrating Proof of Possession

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc9449.html

Relevant topics:

```text
DPoP
Proof of Possession
Public / Private Key
Sender-Constrained Access Tokens
Sender-Constrained Refresh Tokens
```

This specification is relevant to the sender-constraining portion of this lecture.

---

## 47.4 RFC 7009 — OAuth 2.0 Token Revocation

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc7009.html

Relevant topics:

```text
Token Revocation Endpoint
Refresh Token Revocation
Token Type Hint
Authorization Grant Revocation
```

This specification supplements OAuth 2.0 with an explicit mechanism for Client-initiated token revocation.

---

## 47.5 RFC 10017 — OAuth 2.0 for Browser-Based Applications

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice.

Official source:

https://www.rfc-editor.org/rfc/rfc10017.html

Relevant topics:

```text
Browser-based OAuth Clients
Refresh Tokens in browser applications
Refresh Token leakage
Refresh Token rotation
Sender-constrained Refresh Tokens
Maximum Refresh Token lifetime
Refresh Token inactivity expiration
Secure browser application architecture
```

This is particularly important because this learning track will eventually implement browser-based OAuth Clients.

RFC 10017 explicitly requires browser-based deployments issuing Refresh Tokens to follow the Refresh Token requirements in RFC 9700. It also adds requirements around Refresh Token lifetime and rotated-token lifetime. 

---

## 47.6 Source Currency / Update Check

The applicable source set was checked before drafting.

```text
RFC 6749
    │
    └── Foundational Refresh Token specification
            │
            ▼
RFC 9700
    │
    └── Current OAuth Security BCP
            │
            ├── Refresh Token risk assessment
            ├── Scope/resource binding
            ├── Replay protection
            ├── Rotation
            └── Sender Constraint
                    │
          ┌─────────┴─────────┐
          │                   │
      RFC 9449             RFC 7009
        DPoP                Revocation
          │
          └─────────┬─────────┘
                    │
                    ▼
               RFC 10017
                    │
                    └── Browser-specific
                        Refresh Token requirements
```

The important update is that Refresh Tokens should not be taught using RFC 6749 alone.

The modern security model is:

```text
RFC 6749
    +
RFC 9700
    +
RFC 9449
    +
RFC 7009
    +
RFC 10017
        ↓
Modern Refresh Token Security Model
```

In particular, RFC 9700 changes the practical baseline for public Clients by requiring replay detection through Refresh Token rotation or sender-constraining. RFC 10017 applies these requirements specifically to browser-based applications and adds explicit lifetime requirements. 

---

# 48. Final Mental Model

```text
Authorization
      ↓
Authorization Code
      ↓
Token Exchange
      ↓
┌───────────────────────────┐
│ Access Token              │
│                           │
│ → Resource Server         │
└───────────────────────────┘

┌───────────────────────────┐
│ Refresh Token             │
│                           │
│ → Token Endpoint          │
│                           │
│ → New Access Token        │
└───────────────────────────┘
              │
              ▼
     Security Lifecycle
              │
     ┌────────┼────────┐
     │        │        │
 Rotation  Sender   Expiration
           Constraint
     │        │        │
     └────────┼────────┘
              ▼
          Revocation
              ▼
       Secure Lifecycle
```

The key principle is:

```text
A Refresh Token extends the ability
to obtain authorization tokens.

It does not itself represent permission
to access the protected resource.
```
