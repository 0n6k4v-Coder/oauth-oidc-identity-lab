# Lecture 07 — Refresh Token

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Unit:** OAuth 2.0
> **Prerequisite:** Authorization Code, Token Exchange, and Access Token

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what a Refresh Token is and why OAuth uses it.
* Distinguish a Refresh Token from an Access Token.
* Explain why Refresh Tokens are high-value credentials.
* Describe the Refresh Token lifecycle.
* Construct a Refresh Token request correctly.
* Explain the relationship between Refresh Tokens, scopes, and resources.
* Explain Refresh Token rotation.
* Explain Refresh Token replay detection.
* Distinguish Refresh Token rotation from sender-constrained Refresh Tokens.
* Understand the different security requirements for confidential and public clients.
* Understand Refresh Token expiration and inactivity policies.
* Explain why a stolen Refresh Token can be more dangerous than a stolen Access Token.
* Apply the current OAuth security guidance from RFC 9700 when designing Refresh Token handling.
* Understand the additional requirements applicable to browser-based applications.

---

# 2. Why Does OAuth Need a Refresh Token?

An Access Token is intentionally allowed to have a relatively short lifetime.

For example:

```text
Access Token
    lifetime = 10 minutes
```

This is desirable because a stolen Access Token should have only a limited period of usefulness.

But this creates a usability problem.

Without a Refresh Token:

```text
Access Token expires
        │
        ▼
Client needs a new authorization
        │
        ▼
User may need to authorize again
```

A Refresh Token solves this problem.

```text
                    Authorization Server
                           │
                           │ authorization
                           ▼
                         Client
                           │
                 ┌─────────┴─────────┐
                 │                   │
          Access Token         Refresh Token
                 │                   │
                 ▼                   ▼
        Resource Server       Authorization Server
```

The Client can use the Refresh Token to obtain a new Access Token without requiring the End-User to repeat the complete authorization interaction.

RFC 6749 defines a Refresh Token as a credential used to obtain Access Tokens and explicitly states that Refresh Tokens are intended for use only with the Authorization Server and are never sent to Resource Servers.

---

# 3. Access Token vs Refresh Token

The two credentials have fundamentally different purposes.

## Access Token

```text
Purpose:
    Access protected resources

Used with:
    Resource Server
```

Conceptually:

```text
Client
   │
   │ Access Token
   ▼
Resource Server
```

---

## Refresh Token

```text
Purpose:
    Obtain a new Access Token

Used with:
    Authorization Server
```

Conceptually:

```text
Client
   │
   │ Refresh Token
   ▼
Authorization Server
```

Therefore:

```text
Access Token
    →
Resource Server

Refresh Token
    →
Authorization Server
```

A Refresh Token must **never be presented to a Resource Server as if it were an Access Token**. RFC 6749 explicitly distinguishes the two credentials this way.

---

# 4. Why Refresh Tokens Are High-Value Credentials

A common mistake is to think:

```text
Access Token = dangerous
Refresh Token = less dangerous
```

The security model is actually closer to:

```text
Refresh Token
      │
      ▼
Can obtain new Access Tokens
      │
      ▼
Can potentially regain access
      │
      ▼
Protected Resources
```

Suppose an Access Token lasts:

```text
10 minutes
```

while a Refresh Token lasts:

```text
8 hours
```

An attacker who steals the Access Token may have a limited attack window.

An attacker who steals the Refresh Token may repeatedly obtain new Access Tokens.

Therefore:

```text
Refresh Token
    =
longer-lived credential
    +
token issuance capability
```

RFC 9700 explicitly identifies Refresh Tokens as attractive targets because an attacker who successfully exfiltrates and replays one can mint Access Tokens and access Resource Servers on behalf of the resource owner.

---

# 5. The Refresh Token Lifecycle

The lifecycle can be represented as:

```text
Authorization
      │
      ▼
Authorization Server
      │
      │ issues
      ▼
Refresh Token
      │
      │ securely stored
      ▼
Client
      │
      │ refresh request
      ▼
Authorization Server
      │
      │ validate
      ▼
New Access Token
      │
      ├───────────────┐
      │               │
      ▼               ▼
Resource Server   New Refresh Token
                      │
                      ▼
                   Client
```

This lifecycle can repeat:

```text
Refresh
   ↓
Access Token
   ↓
Expires
   ↓
Refresh
   ↓
Access Token
   ↓
Expires
   ↓
Refresh
```

The critical question is:

> What happens to the old Refresh Token when the Client refreshes?

This is where modern OAuth security becomes important.

---

# 6. Refresh Token Is Optional

OAuth does not require every authorization server to issue Refresh Tokens.

RFC 6749 makes Refresh Token issuance optional.

Conceptually:

```text
Authorization Server
        │
        ├── Issue Access Token only
        │
        └── Issue Access Token
                +
              Refresh Token
```

The decision should depend on the application's requirements and security risk.

RFC 9700 goes further and states that Authorization Servers **MUST determine, based on a risk assessment, whether to issue Refresh Tokens to a particular client**.

Therefore:

```text
Refresh Token
    ≠
automatic requirement
```

Instead:

```text
Need for long-lived authorization
        +
Client security characteristics
        +
Threat model
        ↓
Decision to issue Refresh Token
```

---

# 7. Refresh Token Is Not a Session

Another important distinction:

```text
Refresh Token
    ≠
HTTP Session
```

A session may represent:

```text
Browser
    ↔
Application
```

A Refresh Token represents authorization that can be used to obtain new Access Tokens.

Conceptually:

```text
Application Session
    =
application state

Refresh Token
    =
OAuth authorization credential
```

They may participate in the same overall authentication architecture, but they are not interchangeable concepts.

---

# 8. The Basic Refresh Request

When the Access Token becomes invalid or expires, the Client can send a request to the Token Endpoint.

The request uses:

```text
grant_type=refresh_token
```

For example:

```http
POST /token HTTP/1.1
Host: authorization.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=REFRESH_TOKEN
```

RFC 6749 defines `grant_type=refresh_token` as the required parameter value for the Refresh Token grant.

---

# 9. Scope During Refresh

A Client may request a scope during refresh.

For example:

```http
grant_type=refresh_token&
refresh_token=REFRESH_TOKEN&
scope=profile.read
```

However, the Client cannot use the Refresh Token to escalate privileges arbitrarily.

The requested scope:

```text
MUST NOT
```

include scopes that were not originally granted by the resource owner.

RFC 6749 explicitly defines this restriction.

Conceptually:

```text
Original authorization
        │
        ▼
Granted scope
        │
        ▼
Refresh Token
        │
        ▼
Requested scope during refresh
        │
        ▼
Must remain within authorization boundary
```

This prevents:

```text
profile.read
      ↓
Refresh request
      ↓
admin.write
```

from becoming a privilege escalation mechanism.

---

# 10. Refresh Tokens Are Bound to Authorization

A Refresh Token does not represent unlimited authorization.

RFC 9700 clarifies that issued Refresh Tokens must be bound to the scope and resource servers consented to by the resource owner.

Conceptually:

```text
Authorization Grant
       │
       ├── Scope
       │
       └── Resource Servers
              │
              ▼
        Refresh Token
```

This creates an authorization boundary around the Refresh Token.

The Refresh Token should not allow a legitimate Client to expand the authorization beyond what was granted.

---

# 11. Refresh Token and Client Binding

A Refresh Token is associated with the Client to which it was issued.

For confidential clients, RFC 6749 requires the Authorization Server to authenticate the Client during refresh and ensure that the Refresh Token was issued to that authenticated Client.

Conceptually:

```text
Refresh Token
      │
      ▼
client_id = client-123
      │
      ▼
Client authenticates as client-123
      │
      ▼
Authorization Server
      │
      ▼
Accept / Reject
```

The important relationship is:

```text
Refresh Token
      ↕
Client
```

An attacker should not be able to take a Refresh Token issued to one Client and simply use it as another Client.

---

# 12. Confidential vs Public Clients

The security model differs depending on Client type.

## Confidential Client

A confidential Client can securely authenticate to the Authorization Server.

For example:

```text
Backend Application
       │
       │ client authentication
       ▼
Authorization Server
```

The Authorization Server can therefore verify the Client identity during token refresh.

---

## Public Client

A public Client cannot safely keep a client secret.

Examples include:

```text
Native Application
Browser-Based Application
```

A static client secret embedded in such an application cannot be treated as confidential.

Therefore:

```text
Public Client
     │
     ├── cannot rely on static client secret
     │
     └── requires additional protection
```

RFC 9700 specifically strengthens the requirements for Refresh Token replay protection for public clients.

---

# 13. The Fundamental Refresh Token Threat

Consider:

```text
Legitimate Client
      │
      │ Refresh Token
      ▼
Authorization Server
```

Now assume an attacker steals the Refresh Token:

```text
                    ┌── Legitimate Client
                    │
Refresh Token ──────┤
                    │
                    └── Attacker
```

The attacker attempts:

```text
Attacker
   │
   │ stolen Refresh Token
   ▼
Authorization Server
   │
   │ issue Access Token
   ▼
Attacker
```

If successful:

```text
Stolen Refresh Token
        ↓
New Access Token
        ↓
Resource Server
```

This is a Refresh Token replay attack.

---

# 14. Why Refresh Token Replay Is Different

An Access Token replay attack looks like:

```text
Stolen Access Token
       │
       ▼
Resource Server
```

A Refresh Token replay attack looks like:

```text
Stolen Refresh Token
       │
       ▼
Authorization Server
       │
       ▼
New Access Token
       │
       ▼
Resource Server
```

The second attack gives the attacker a mechanism to obtain additional Access Tokens.

Therefore:

```text
Refresh Token
    =
credential capable of creating
new access credentials
```

This is why RFC 9700 places specific replay-detection requirements on public clients.

---

# 15. Refresh Token Rotation

One of the primary defenses is:

```text
Refresh Token Rotation
```

Instead of:

```text
RT1
 │
 ├── refresh
 │
 ├── refresh
 │
 └── refresh
```

the Authorization Server issues a new Refresh Token each time:

```text
RT1
 │
 │ refresh
 ▼
RT2
 │
 │ refresh
 ▼
RT3
 │
 │ refresh
 ▼
RT4
```

The previous Refresh Token becomes invalid.

Conceptually:

```text
RT1
 ↓
invalid

RT2
 ↓
valid

RT3
 ↓
valid
```

RFC 9700 defines this as one of the two required mechanisms for detecting Refresh Token replay by malicious actors for public clients.

---

# 16. Rotation Creates a Token Family

Rotation is more useful when the Authorization Server maintains the relationship between tokens.

Conceptually:

```text
             Grant
               │
               ▼
             RT1
               │
               ▼
             RT2
               │
               ▼
             RT3
               │
               ▼
             RT4
```

This can be considered a:

```text
Refresh Token Family
```

The Authorization Server can track:

```text
RT1 → RT2 → RT3 → RT4
```

This allows it to recognize reuse of an invalidated token.

RFC 9700 states that information about the relationship between rotated Refresh Tokens is retained so the Authorization Server can detect replay and revoke the active Refresh Token when a compromised token is reused.

---

# 17. Replay Detection

Consider the normal sequence:

```text
Client
  │
  │ RT1
  ▼
Authorization Server
  │
  ├── invalidate RT1
  └── issue RT2
```

The legitimate Client now has:

```text
RT2
```

Suppose an attacker previously stole:

```text
RT1
```

The attacker later sends:

```text
Attacker
  │
  │ RT1
  ▼
Authorization Server
```

The Authorization Server sees:

```text
RT1
    =
already invalidated
```

This is evidence of possible compromise.

The Authorization Server can then invalidate the active Refresh Token associated with the token family.

Conceptually:

```text
RT1 reused
    │
    ▼
Replay detected
    │
    ▼
Revoke active token family
    │
    ▼
Legitimate Client must re-authorize
```

This is the fundamental security value of Refresh Token Rotation.

---

# 18. Why Rotation Works

Without rotation:

```text
RT1
 │
 ├── Client
 ├── Attacker
 ├── Client
 ├── Attacker
 └── ...
```

The Authorization Server may have difficulty distinguishing legitimate use from replay.

With rotation:

```text
RT1 → RT2 → RT3 → RT4
```

the old token becomes a detection mechanism.

If:

```text
RT2 = current
```

and someone presents:

```text
RT1
```

the server knows that an old credential has been reused.

Therefore:

```text
Rotation
    +
Reuse Detection
    ↓
Replay Detection
```

---

# 19. Rotation Is Not Encryption

Refresh Token Rotation does not protect the Refresh Token from being stolen.

It changes the consequences of reuse.

For example:

```text
Attacker steals RT1
```

can still be dangerous.

The security property is:

```text
If RT1 is reused after rotation,
the Authorization Server can detect it.
```

Therefore:

```text
Rotation
    ≠
prevention of theft
```

Instead:

```text
Rotation
    =
replay detection + containment
```

This distinction is important.

---

# 20. Sender-Constrained Refresh Tokens

The second major mechanism defined by RFC 9700 for public clients is:

```text
Sender-Constrained Refresh Tokens
```

Instead of relying on rotation, the Authorization Server can cryptographically bind the Refresh Token to a particular Client instance.

Conceptually:

```text
Refresh Token
      +
Client Key
      │
      ▼
Authorization Server
```

The Client must prove possession of the corresponding key when using the Refresh Token.

An attacker who steals only the Refresh Token should not be able to successfully replay it.

RFC 9700 explicitly identifies sender-constrained Refresh Tokens as an alternative to rotation for public clients.

---

# 21. DPoP-Bound Refresh Tokens

DPoP can be used to sender-constrain tokens.

The Client owns:

```text
Private Key
+
Public Key
```

The Refresh Token is associated with the public key.

During token refresh:

```text
Client
 │
 ├── Refresh Token
 │
 └── DPoP Proof
 │
 ▼
Authorization Server
```

The Authorization Server verifies that the Client possesses the key associated with the token.

Conceptually:

```text
Stolen Refresh Token
        │
        │ without private key
        ▼
      Reject
```

RFC 9449 defines DPoP as a mechanism for sender-constraining OAuth tokens through proof of possession. RFC 9700 explicitly identifies DPoP as an example of a mechanism suitable for sender-constrained Refresh Tokens.

---

# 22. Rotation vs Sender Constraint

These mechanisms solve the same high-level problem in different ways.

| Property                 | Rotation                  | Sender-Constrained          |
| ------------------------ | ------------------------- | --------------------------- |
| Main mechanism           | Change token on every use | Bind token to key           |
| Detects old-token reuse  | Yes                       | Not the primary mechanism   |
| Requires key management  | No                        | Yes                         |
| Public-client protection | Yes                       | Yes                         |
| Can reduce replay        | Yes                       | Yes                         |
| Main idea                | Detect reuse              | Require proof of possession |

Conceptually:

```text
Rotation

RT1 → RT2 → RT3
 │
 └── reuse detected
```

versus:

```text
Sender Constraint

RT1 + Private Key
       │
       ▼
     valid

RT1 without key
       │
       ▼
     reject
```

RFC 9700 permits either approach for the required public-client replay protection.

---

# 23. Refresh Token Lifetime

A Refresh Token should not necessarily live forever.

RFC 9700 recommends that Refresh Tokens expire when the Client has been inactive for some period of time.

Browser-based applications receive even more explicit guidance in RFC 10017:

The Authorization Server must either:

```text
set a maximum Refresh Token lifetime
```

or:

```text
expire the Refresh Token
if it has not been used for some period of time
```

when issuing Refresh Tokens to browser-based applications.

Therefore:

```text
Refresh Token
      │
      ├── absolute lifetime
      │
      └── inactivity lifetime
```

may both be relevant.

---

# 24. Absolute Lifetime vs Inactivity Lifetime

These are different concepts.

## Absolute Lifetime

Example:

```text
Issued:
09:00

Expires:
17:00
```

The Refresh Token cannot be used after 17:00.

---

## Inactivity Lifetime

Example:

```text
Last used:
09:00
```

Policy:

```text
Expire after 2 hours of inactivity
```

If the Client does not use the Refresh Token until:

```text
11:01
```

it may be expired.

Conceptually:

```text
Absolute lifetime
        +
Inactivity lifetime
        ↓
Refresh Token validity
```

The appropriate values depend on risk and application requirements.

---

# 25. Rotation Must Not Extend the Overall Lifetime Indefinitely

This is a particularly important modern clarification.

Suppose:

```text
Initial Refresh Token
issued at 09:00

Absolute expiration:
17:00
```

The Client rotates:

```text
RT1 → RT2
```

at:

```text
16:00
```

The server should not simply create:

```text
RT2 expiration = 00:00 next day
```

if the original token had a pre-established expiration of 17:00.

RFC 10017 explicitly requires that when browser-based applications use rotated Refresh Tokens, a newly issued token must not extend the lifetime beyond the initial Refresh Token's pre-established expiration.

Conceptually:

```text
Initial:
RT1 ───────────────────────┐
                           │
                           ▼
                         17:00
                           │
RT2 ───────────────────────┘
```

not:

```text
RT1 ───────────────────────┐
                           │
                           ▼
                         17:00

RT2 ────────────────────────────────► next day
```

This prevents rotation from accidentally creating an indefinitely renewable credential.

---

# 26. Refresh Token Storage

Refresh Tokens are credentials and must be protected.

RFC 6749 establishes the baseline requirement that Refresh Tokens must be kept confidential in transit and storage and shared only between the Authorization Server and the Client to which they were issued.

Conceptually:

```text
Refresh Token
      │
      ├── Protect in transit
      │
      ├── Protect at rest
      │
      ├── Do not log
      │
      └── Do not expose unnecessarily
```

A Refresh Token should be treated as a high-value secret.

---

# 27. Refresh Tokens Must Use TLS

Refresh Token requests must be protected in transit.

Conceptually:

```text
Client
   │
   │ HTTPS
   │
   │ Refresh Token
   ▼
Authorization Server
```

not:

```text
Client
   │
   │ HTTP
   │
   │ Refresh Token