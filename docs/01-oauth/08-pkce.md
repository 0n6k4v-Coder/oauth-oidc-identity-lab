# Lecture 08 — OAuth 2.0 PKCE

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Authorization Code Security
> **Prerequisite:** Understanding of Authorization Requests, Authorization Codes, Token Exchange, and Client Types

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what PKCE is and why it was introduced.
* Explain the relationship between `code_verifier` and `code_challenge`.
* Explain how PKCE binds an Authorization Request to the later Token Request.
* Understand how PKCE protects an intercepted Authorization Code.
* Understand how PKCE protects against Authorization Code injection.
* Explain the `S256` code challenge method.
* Understand why `S256` is preferred over `plain`.
* Explain the responsibilities of the Client and Authorization Server during PKCE.
* Understand PKCE downgrade attacks and how to prevent them.
* Understand why PKCE is transaction-specific.
* Understand how PKCE relates to CSRF protection.
* Distinguish PKCE from Client authentication.
* Distinguish PKCE from `state`.
* Understand the current PKCE requirements for public Clients.
* Understand the current PKCE requirements for browser-based applications.
* Recognize the limitations of PKCE after Client or browser-environment compromise.

---

# 2. Why PKCE Exists

The Authorization Code Grant has an important security property:

```text
Authorization Code
        ↓
Token Endpoint
        ↓
Access Token
```

However, the Authorization Code can potentially be intercepted before it reaches the legitimate Client.

For example:

```text
Authorization Server
        │
        │ Authorization Code
        ▼
Browser / User Agent
        │
        │ code
        ├──────────────► Attacker
        │
        ▼
Client
```

The attacker now possesses:

```text
Authorization Code
```

If the attacker can successfully redeem that code:

```text
Attacker
   │
   │ Authorization Code
   ▼
Token Endpoint
   │
   ▼
Access Token
```

the attacker may obtain the authorization result.

PKCE introduces an additional secret that is known only to the Client instance that initiated the transaction.

That secret is:

```text
code_verifier
```

The Authorization Server receives only a derived value during the Authorization Request:

```text
code_challenge
```

Later, during Token Exchange, the Client proves possession of the original verifier.

This creates:

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
        │ verify
        ▼
Token Response
```

This is the fundamental idea of PKCE.

RFC 7636 defines this mechanism, and RFC 9700 makes PKCE part of the current OAuth security baseline. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc7636.html))

---

# 3. PKCE Is Proof of Possession of a Transaction Secret

The important conceptual shift is:

```text
Without PKCE

Authorization Code
      ↓
Possession may be enough
```

versus:

```text
With PKCE

Authorization Code
      +
code_verifier
      ↓
Successful redemption
```

The Authorization Code alone is therefore insufficient for a compliant PKCE-protected transaction.

The Client must prove:

```text
"I am the same Client instance
that started this authorization transaction."
```

PKCE does not identify the Client in the same way as a Client Secret.

Instead, it binds the authorization request to the token request.

---

# 4. The Two PKCE Values

PKCE uses two main values:

```text
code_verifier
code_challenge
```

The relationship is:

```text
code_verifier
      │
      │ transform
      ▼
code_challenge
```

The Client generates the `code_verifier`.

The Client sends the resulting `code_challenge` in the Authorization Request.

Later, the Client sends the original `code_verifier` in the Token Request.

The Authorization Server verifies the relationship.

---

# 5. `code_verifier`

The `code_verifier` is a high-entropy, cryptographically random string generated for the authorization transaction.

Conceptually:

```text
Client

generate random value

code_verifier
    =
RANDOM_TRANSACTION_SECRET
```

The verifier should be:

```text
Unique per transaction
Unpredictable
Sufficiently high entropy
Kept confidential by the Client
```

PKCE is therefore not:

```text
verifier = "12345"
```

or:

```text
verifier = username
```

or:

```text
verifier = constant application value
```

The verifier must be transaction-specific.

RFC 7636 defines the `code_verifier` requirements, while RFC 9700 explicitly requires PKCE challenges to be transaction-specific and securely bound to the Client and user agent involved in the transaction. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc7636.html))

---

# 6. `code_challenge`

The Client transforms the verifier into a challenge.

For modern deployments using `S256`:

```text
code_challenge
    =
BASE64URL(
    SHA-256(
        code_verifier
    )
)
```

Conceptually:

```text
code_verifier
      │
      ▼
   SHA-256
      │
      ▼
Base64url
      │
      ▼
code_challenge
```

The Client sends the challenge during authorization.

The Client does not send the verifier during the Authorization Request.

---

# 7. Why Not Send the Verifier Directly?

Suppose the Client sends:

```text
code_verifier
```

directly in the Authorization Request.

An attacker that can observe the request could obtain:

```text
Authorization Code
        +
code_verifier
```

and potentially redeem the code.

PKCE instead sends a derived value:

```text
code_challenge
```

The original verifier remains with the Client.

Therefore:

```text
Authorization Request
    → code_challenge

Token Request
    → code_verifier
```

This creates the proof relationship required at token exchange.

---

# 8. The `S256` Method

PKCE supports challenge methods identified by:

```text
code_challenge_method
```

The modern recommendation is:

```text
S256
```

The flow is:

```text
code_verifier
      ↓
SHA-256
      ↓
BASE64URL
      ↓
code_challenge
```

Then:

```http
code_challenge_method=S256
```

The Authorization Server stores the challenge together with the authorization transaction.

Later, it calculates the challenge from the supplied verifier and compares the values.

RFC 9700 identifies `S256` as the currently applicable method that does not expose the verifier in the authorization request. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 9. The `plain` Method

PKCE also defines:

```text
plain
```

Under `plain`:

```text
code_challenge
    =
code_verifier
```

This does not provide the same protection against attackers who can read the authorization request.

For example:

```text
Authorization Request
        │
        ├── code_challenge = SECRET
        └── method = plain
```

An attacker who can read the request obtains the verifier directly.

For this reason, current OAuth security guidance strongly favors:

```text
S256
```

and RFC 9700 states that Clients should use a code challenge method that does not expose the verifier in the Authorization Request; currently, `S256` is the only such method. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 10. The PKCE Authorization Request

A simplified Authorization Request may look like:

```text
https://authorization.example.com/authorize?
    response_type=code&
    client_id=client-123&
    redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
    scope=read&
    state=STATE_VALUE&
    code_challenge=CODE_CHALLENGE&
    code_challenge_method=S256
```

The key PKCE parameters are:

```text
code_challenge
code_challenge_method
```

The verifier is not included.

---

# 11. The Authorization Server Stores the Challenge

The Authorization Server associates the challenge with the authorization transaction.

Conceptually:

```text
Authorization Transaction

Client
    │
    ├── client_id
    ├── redirect_uri
    ├── scope
    ├── state
    └── code_challenge
             │
             ▼
      Authorization Server
             │
             ▼
      Authorization Code
             +
      stored PKCE context
```

The Authorization Code is therefore associated with the challenge.

The internal representation is implementation-specific.

It may be:

```text
Database
Cache
Encrypted server-side state
Signed authorization-code structure
```

The protocol requirement is the security relationship, not a particular storage mechanism.

---

# 12. The Token Request

During Token Exchange, the Client sends:

```text
grant_type=authorization_code
code=AUTHORIZATION_CODE
code_verifier=CODE_VERIFIER
```

Conceptually:

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
code_verifier=CODE_VERIFIER
```

Depending on the Client and deployment, the request may additionally include:

```text
redirect_uri
client_id
Client authentication
```

The important PKCE element is:

```text
code_verifier
```

---

# 13. How the Authorization Server Verifies PKCE

The server has:

```text
Stored code_challenge
```

and receives:

```text
code_verifier
```

For `S256`, it computes:

```text
BASE64URL(SHA-256(code_verifier))
```

Then compares:

```text
Calculated Challenge
          =
Stored Challenge
```

Conceptually:

```text
Stored code_challenge
          │
          │ compare
          ▼
BASE64URL(
    SHA-256(
        supplied code_verifier
    )
)
          │
     ┌────┴────┐
     │         │
   Match    Mismatch
     │         │
     ▼         ▼
Continue      Reject
```

---

# 14. What PKCE Protects

PKCE primarily protects the authorization code from being redeemed by an attacker who does not possess the verifier.

The simplified attack is:

```text
Attacker
   │
   │ stolen Authorization Code
   ▼
Token Endpoint
```

The server requires:

```text
code_verifier
```

The attacker does not possess it.

Therefore:

```text
Authorization Code
    +
Wrong / missing verifier
        ↓
PKCE verification failure
        ↓
Reject
```

This is the fundamental PKCE security property.

---

# 15. Authorization Code Interception

One of the original motivations for PKCE was protection of authorization-code interception.

Conceptually:

```text
Authorization Server
        │
        │ Code
        ▼
User Agent
        │
        ├──────────────► Attacker
        │                  Code
        │
        ▼
Client
```

The attacker has:

```text
Code
```

but not:

```text
code_verifier
```

Therefore:

```text
Attacker
   ↓
Token Endpoint
   ↓
PKCE verification
   ↓
Reject
```

RFC 7636 was originally designed around this problem, and current OAuth guidance extends the use of PKCE to modern OAuth clients broadly. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc7636.html))

---

# 16. Authorization Code Injection

PKCE also protects against a different class of attack:

```text
Authorization Code Injection
```

Consider:

```text
Attacker
   │
   │ obtains Code A
   ▼
Authorization flow
   │
   │ victim Client receives Code A
   ▼
Victim Client
   │
   │ sends Code A + its verifier
   ▼
Token Endpoint
```

If Code A was created using a different challenge:

```text
Attacker's code_challenge
        ≠
Victim's code_verifier-derived challenge
```

then:

```text
PKCE verification
        ↓
Mismatch
        ↓
Reject
```

RFC 9700 explicitly identifies PKCE as a defense against authorization-code injection. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 17. PKCE Binds the Transaction

The most useful mental model is:

```text
Authorization Request
        │
        │ code_challenge
        ▼
Authorization Transaction
        │
        │ bind
        ▼
Authorization Code
        │
        │ later
        ▼
Token Request
        │
        │ code_verifier
        ▼
Verification
```

The verifier therefore proves continuity:

```text
Transaction Started By Client
            =
Transaction Redeemed By Client
```

This is why PKCE is more than simply:

```text
"an extra parameter"
```

It is a transaction-binding mechanism.

---

# 18. PKCE Is Transaction-Specific

A Client must not reuse one verifier across transactions.

Bad:

```text
Every transaction
    ↓
code_verifier = CONSTANT_VALUE
```

Good:

```text
Transaction A
    ↓
Verifier A

Transaction B
    ↓
Verifier B

Transaction C
    ↓
Verifier C
```

Current OAuth Security BCP explicitly requires PKCE challenges to be transaction-specific and securely bound to the Client and user agent in which the transaction was started. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 19. PKCE and `state`

PKCE and `state` can look similar because both participate in transaction security.

They are not the same mechanism.

## PKCE

```text
code_challenge
        ↓
code_verifier
        ↓
Authorization Code binding
```

## `state`

```text
state
  ↓
Authorization response correlation
  +
CSRF defense
```

They protect different properties.

Current OAuth security guidance recognizes that PKCE can provide strong CSRF protection when properly used, but `state` remains relevant depending on the client architecture and protocol context. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 20. PKCE and CSRF

A modern OAuth Client should deliberately choose its CSRF protection.

RFC 9700 explains that PKCE can provide CSRF protection when the challenge is:

```text
Unpredictable
Transaction-specific
Correctly bound
```

For example:

```text
Transaction
    ↓
Random verifier
    ↓
S256 challenge
    ↓
Authorization request
```

An attacker cannot simply substitute an unrelated authorization response without causing the PKCE check to fail.

However, Clients must still consider their complete architecture and threat model.

PKCE should not be implemented with:

```text
constant verifier
```

or:

```text
predictable verifier
```

because that destroys the binding property.

---

# 21. PKCE Is Not Client Authentication

This distinction is critical.

PKCE answers:

```text
"Does this token request possess
the secret generated for this transaction?"
```

Client authentication answers:

```text
"Which registered Client is making this request?"
```

Therefore:

```text
PKCE
    ≠
Client Authentication
```

For example:

```text
Public Client
    +
PKCE
```

can protect an Authorization Code even though the Client cannot keep a static secret confidential.

A confidential Client may also use:

```text
Client Authentication
    +
PKCE
```

for additional protection.

RFC 9700 recommends PKCE for confidential Clients as well because it provides protection against authorization-code misuse and injection. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 22. PKCE Does Not Replace Client Registration

PKCE does not mean:

```text
No client_id needed
```

or:

```text
Client registration unnecessary
```

The Client still has:

```text
client_id
redirect_uri
registered configuration
```

depending on the deployment.

PKCE adds a security binding to the authorization transaction.

The complete model may therefore be:

```text
Registered Client
       +
Authorization Transaction
       +
PKCE
       ↓
Token Request
```

---

# 23. PKCE Downgrade Attacks

A serious implementation problem occurs when an Authorization Server supports PKCE but allows a transaction to silently fall back to no PKCE.

For example:

```text
Authorization Request

code_challenge = ABC
```

but the server somehow processes the transaction as:

```text
PKCE not required
```

or allows:

```text
Token Request
without corresponding PKCE binding
```

This can weaken the security property the Client expected.

Current OAuth Security BCP requires Authorization Servers to mitigate PKCE downgrade attacks.

In particular, a Token Request containing `code_verifier` should only be accepted when a corresponding `code_challenge` was present in the authorization request. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 24. Authorization Server PKCE Requirements

Modern Authorization Servers must support PKCE.

For public Clients:

```text
Public Client
      ↓
PKCE
      ↓
Required
```

The Authorization Server must:

```text
Support PKCE
Accept the challenge
Bind it to the transaction
Require the verifier at token exchange
Validate the verifier
```

RFC 9700 explicitly requires Authorization Servers to support PKCE and requires enforcement when a code challenge was supplied. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 25. Public Client PKCE Requirement

For public Clients:

```text
PKCE
   =
Required Security Control
```

This is particularly important for:

```text
Browser-based applications
Native applications
```

because these Client types cannot depend on a static secret remaining confidential.

The modern sequence is therefore:

```text
Public Client
     ↓
Authorization Code
     +
PKCE
     ↓
Token Exchange
```

not:

```text
Public Client
     ↓
Authorization Code
     ↓
No proof
```

RFC 9700 establishes this modern baseline. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 26. Browser-Based Applications

This is directly relevant to this repository because our Client is a React application running in a browser.

Current browser-based OAuth guidance is defined by RFC 10017, published in August 2026.

It states that browser-based applications acting as public Clients and using the Authorization Code Grant:

```text
MUST implement PKCE
```

and:

```text
Authorization Servers
MUST support and enforce PKCE
```

RFC 10017 identifies the modern browser best practice as:

```text
Authorization Code
        +
PKCE
```

instead of the historical Implicit Grant model. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 27. PKCE and Browser Security

A browser-based Client operates in an environment where malicious JavaScript, XSS, and compromised application code can be serious threats.

PKCE helps with:

```text
Authorization Code interception
Authorization Code injection
```

but does not make the browser environment trustworthy.

For example:

```text
XSS
  ↓
Attacker executes code
  ↓
Compromised Client runtime
```

At that point, the attacker may be able to interfere with the transaction itself.

Therefore:

```text
PKCE
    +
Browser Security
    +
Content Security Policy
    +
Secure Application Dependencies
    +
CSRF Protection
```

must be considered together.

RFC 10017 explicitly treats malicious JavaScript as a major threat to browser-based OAuth applications. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 28. PKCE Does Not Provide 100% Security

PKCE significantly improves Authorization Code security, but it is not an absolute security guarantee.

For example:

```text
Attacker steals Code
        +
No verifier
        ↓
PKCE blocks redemption
```

But:

```text
Attacker compromises Client runtime
        ↓
May obtain or use verifier
```

At that point the attacker may be able to participate in the transaction as the Client.

Therefore:

```text
PKCE
    =
Strong transaction binding
    ≠
Complete Client security
```

This is an important security boundary.

---

# 29. What Happens if Both Code and Verifier Leak?

Suppose an attacker obtains:

```text
Authorization Code
        +
code_verifier
```

Then:

```text
PKCE
    ↓
Cannot distinguish legitimate
from attacker-controlled redeemer
```

The PKCE protection is effectively defeated for that transaction.

This illustrates why:

```text
Protecting the verifier
```

is essential.

The verifier is not a public value.

---

# 30. What Happens if the Authorization Request Leaks?

If the Client uses:

```text
S256
```

the Authorization Request reveals:

```text
code_challenge
```

but not:

```text
code_verifier
```

Therefore:

```text
Leaked Authorization Request
        ↓
Attacker gets challenge
        ↓
Still does not know verifier
        ↓
PKCE remains effective
```

This is one reason why `S256` is preferred.

With `plain`:

```text
code_challenge
    =
code_verifier
```

and leakage of the authorization request exposes the verifier directly.

RFC 9700 explicitly highlights this distinction. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 31. PKCE and Replay

PKCE is primarily transaction binding, not a universal replay defense.

It prevents reuse of an Authorization Code by an attacker who lacks the verifier.

But the Authorization Server should also enforce:

```text
Authorization Code
    ↓
Single use
```

Therefore:

```text
PKCE
    +
Single-use Authorization Code
```

is stronger than either concept considered alone.

RFC 9700 discusses both PKCE and authorization-code replay protections. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 32. PKCE and Redirect URI Validation

PKCE does not eliminate the need to validate:

```text
redirect_uri
```

The authorization transaction still needs the correct redirect URI binding.

Therefore:

```text
PKCE
    +
redirect_uri validation
```

should be treated as separate controls.

A secure Authorization Code flow combines multiple transaction-binding properties:

```text
Client
Redirect URI
PKCE
Authorization Code
```

---

# 33. PKCE Security as Defense in Depth

A modern Authorization Code flow can therefore be represented as:

```text
Authorization Request
        │
        ├── client_id
        ├── redirect_uri
        ├── state
        ├── code_challenge
        └── code_challenge_method=S256
        │
        ▼
Authorization Server
        │
        │
        ▼
Authorization Code
        │
        ▼
Token Endpoint
        │
        ├── Client checks
        ├── Code checks
        ├── Redirect URI checks
        ├── PKCE checks
        └── Other applicable checks
        │
        ▼
Token Response
```

No single control is expected to provide complete protection.

---

# 34. A Complete PKCE Transaction

The entire flow:

```text
1. Client generates random code_verifier.

2. Client derives code_challenge using S256.

3. Client sends code_challenge in the
   Authorization Request.

4. Authorization Server stores the PKCE context
   with the authorization transaction.

5. Authorization Server returns an Authorization Code.

6. Client sends the code and code_verifier
   to the Token Endpoint.

7. Authorization Server derives the expected
   challenge from code_verifier.

8. Authorization Server compares the calculated
   challenge with the stored challenge.

9. If they match, continue Token Exchange.

10. If they do not match, reject the request.
```

Conceptually:

```text
                 Client
                   │
                   │ code_verifier
                   │
                   ▼
              SHA-256 + Base64url
                   │
                   ▼
              code_challenge
                   │
                   ▼
            Authorization Request
                   │
                   ▼
          Authorization Server
                   │
                   │ store challenge
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
                   │ calculate
                   ▼
          Compare challenge
                   │
              ┌────┴────┐
              │         │
            Match    Mismatch
              │         │
              ▼         ▼
          Continue     Reject
```

---

# 35. What the Client Must Do

The Client should:

```text
[ ] Generate a fresh verifier for every authorization transaction.

[ ] Keep the verifier associated with the transaction.

[ ] Derive the challenge correctly.

[ ] Use S256.

[ ] Send code_challenge in the authorization request.

[ ] Do not send code_verifier in the authorization request.

[ ] Send code_verifier during token exchange.

[ ] Protect the verifier from disclosure.

[ ] Never use a constant verifier.

[ ] Never log the verifier.
```

---

# 36. What the Authorization Server Must Do

The Authorization Server should:

```text
[ ] Support PKCE.

[ ] Accept supported challenge methods.

[ ] Bind the challenge to the authorization transaction.

[ ] Require the verifier during token exchange when PKCE
    was used.

[ ] Recalculate the expected challenge.

[ ] Compare the expected and supplied values correctly.

[ ] Reject mismatches.

[ ] Prevent PKCE downgrade.

[ ] Keep the PKCE transaction context secure.

[ ] Continue enforcing other Authorization Code
    security requirements.
```

These requirements follow from RFC 7636 and the stronger current guidance in RFC 9700. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 37. What PKCE Does Not Solve

PKCE does not by itself solve:

```text
XSS
Malicious JavaScript
Compromised Client dependencies
Compromised operating system
Compromised browser
Token leakage after token issuance
Incorrect redirect URI validation
Incorrect issuer validation
Weak Client architecture
Improper token storage
```

PKCE specifically strengthens the Authorization Code transaction.

A production OAuth system therefore needs additional controls.

---

# 38. Common Mistakes

## Mistake 1 — Use a Constant Verifier

```text
code_verifier = "my-secret"
```

Wrong.

---

## Mistake 2 — Use `plain` Without Understanding the Risk

```text
code_challenge_method=plain
```

Not the current preferred approach.

Use:

```text
S256
```

instead.

---

## Mistake 3 — Send the Verifier in the Authorization Request

Wrong:

```text
Authorization Request
    ↓
code_verifier=...
```

Correct:

```text
Authorization Request
    ↓
code_challenge=...

Token Request
    ↓
code_verifier=...
```

---

## Mistake 4 — Reuse the Verifier

Wrong:

```text
Transaction A → verifier X
Transaction B → verifier X
```

Correct:

```text
Transaction A → verifier A
Transaction B → verifier B
```

---

## Mistake 5 — Treat PKCE as Client Authentication

```text
PKCE
    =
Client Secret
```

Wrong.

---

## Mistake 6 — Treat PKCE as the Only OAuth Security Control

PKCE does not replace:

```text
redirect_uri validation
state / CSRF protections
Authorization Code single-use
TLS
Client authentication where applicable
secure token handling
browser security
```

---

## Mistake 7 — Allow PKCE Downgrade

Wrong:

```text
code_challenge supplied
        ↓
server ignores it
        ↓
Token request succeeds without verifier
```

Current OAuth Security BCP specifically addresses this threat. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

---

# 39. PKCE in Our Learning Track

The learning progression is now:

```text
Lecture 03
Authorization Request
        ↓
Lecture 04
Authorization Code
        ↓
Lecture 05
Token Exchange
        ↓
Lecture 06
Access Token
        ↓
Lecture 07
Refresh Token
        ↓
Lecture 08
PKCE
```

PKCE appears here because it connects directly to:

```text
Authorization Request
        +
Authorization Code
        +
Token Exchange
```

It is therefore best understood as a security layer spanning multiple protocol stages.

---

# 40. PKCE in Our Lab

In our browser-based React Client:

```text
React Client
        │
        │ generate verifier
        ▼
code_verifier
        │
        │ S256
        ▼
code_challenge
        │
        ▼
Authorization Request
        │
        ▼
Authorization Server
        │
        ▼
Authorization Code
        │
        ▼
React Client
        │
        │ code + verifier
        ▼
Token Endpoint
```

The Client is a browser-based public Client.

Under current guidance:

```text
Browser-based public Client
        +
Authorization Code
        ↓
PKCE required
```

RFC 10017 explicitly requires this model for browser-based public Clients. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

# 41. Knowledge Check

### Question 1

What problem does PKCE solve?

### Question 2

What is the difference between `code_verifier` and `code_challenge`?

### Question 3

Why is the verifier not sent in the Authorization Request?

### Question 4

Why must the verifier be random and transaction-specific?

### Question 5

How does `S256` transform the verifier?

### Question 6

Why is `S256` preferred over `plain`?

### Question 7

How does PKCE protect an intercepted Authorization Code?

### Question 8

How does PKCE protect against Authorization Code injection?

### Question 9

What does the Authorization Server store in relation to PKCE?

### Question 10

When is `code_verifier` sent?

### Question 11

What is a PKCE downgrade attack?

### Question 12

Why is a constant PKCE verifier insecure?

### Question 13

Is PKCE the same as Client authentication?

### Question 14

Is PKCE the same as `state`?

### Question 15

Why must a browser-based public Client use PKCE?

### Question 16

What happens if an attacker obtains the Authorization Code but not the verifier?

### Question 17

What happens if an attacker obtains both the Authorization Code and verifier?

### Question 18

Does PKCE protect against XSS?

### Question 19

Can a production OAuth Client rely on PKCE alone?

### Question 20

Explain the complete PKCE flow from `code_verifier` generation to Token Exchange.

---

# 42. Lecture Summary

PKCE is a security extension to the OAuth 2.0 Authorization Code flow.

Its central mechanism is:

```text
code_verifier
      ↓
S256
      ↓
code_challenge
```

The Client sends:

```text
code_challenge
```

during the Authorization Request.

The Client later sends:

```text
code_verifier
```

during Token Exchange.

The Authorization Server verifies:

```text
S256(code_verifier)
        =
stored code_challenge
```

If they match:

```text
Continue
```

If they do not:

```text
Reject
```

The fundamental security property is:

```text
Authorization Code
        +
Correct code_verifier
        ↓
Successful redemption
```

This prevents an attacker who obtains only the Authorization Code from redeeming it.

PKCE also provides protection against Authorization Code injection because an injected code will normally be associated with a different challenge.

Current OAuth Security BCP requires Authorization Servers to support PKCE and public Clients to use it. It also requires protection against PKCE downgrade attacks and identifies `S256` as the currently applicable challenge method that does not expose the verifier in the authorization request. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9700.html))

For browser-based applications, RFC 10017 makes this explicit:

```text
Browser-based public Client
        +
Authorization Code
        +
PKCE
```

is the current best-practice baseline. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

The most important distinction to retain is:

```text
PKCE
    =
Transaction binding

Client Authentication
    =
Client identity / authentication

state
    =
Authorization response correlation /
CSRF protection
```

PKCE is a strong security control, but:

```text
PKCE
    ≠
100% security
```

A compromised Client runtime can still undermine the security of the transaction.

---

# 43. References

## 43.1 RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Standards Track.

Official source:

https://www.rfc-editor.org/rfc/rfc7636.html

Primary specification for:

```text
code_verifier
code_challenge
code_challenge_method
S256
plain
PKCE Authorization Request
PKCE Token Request
```

Relevant sections:

```text
Section 1
Introduction

Section 3
Protocol Flow

Section 4
Protocol Details

Section 4.1
Client Creates a Code Verifier

Section 4.2
Client Creates the Code Challenge

Section 4.3
Client Sends the Code Challenge with the
Authorization Request

Section 4.5
Client Sends the Authorization Request

Section 4.6
Client Sends the Authorization Code Request

Section 4.6
Server Verifies the Code Verifier
```

---

## 43.2 RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 240).

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

Primary current security source for this lecture.

Relevant topics include:

```text
PKCE support
PKCE for public Clients
PKCE for confidential Clients
S256
Authorization Code interception
Authorization Code injection
PKCE downgrade attacks
Transaction-specific PKCE
CSRF protection
Authorization Code replay
```

RFC 9700 materially updates the practical interpretation of RFC 7636.

In particular:

```text
Authorization Servers MUST support PKCE.

Public Clients MUST use PKCE.

Clients SHOULD use S256.

PKCE challenges MUST be transaction-specific.

Authorization Servers MUST enforce PKCE
when a code challenge was used.

Authorization Servers MUST mitigate
PKCE downgrade attacks.
```

---

## 43.3 RFC 10017 — OAuth 2.0 for Browser-Based Applications

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice.

**Published:** August 2026.

Official source:

https://www.rfc-editor.org/rfc/rfc10017.html

This specification is particularly important for this repository because the Client is a browser-based React application.

Relevant topics:

```text
Browser-based public Clients
Authorization Code Grant
PKCE
Authorization Code injection
CSRF protection
Malicious JavaScript
XSS
CORS
BFF architectures
Token-mediating backends
Browser token exposure
```

RFC 10017 states that browser-based applications that are public Clients and use the Authorization Code Grant MUST implement PKCE, while Authorization Servers MUST support and enforce PKCE for such Clients. ([rfc-editor.org](https://www.rfc-editor.org/rfc/rfc10017.html))

---

## 43.4 RFC 6749 — The OAuth 2.0 Authorization Framework

**Authority:** Internet Engineering Task Force (IETF)

Official source:

https://www.rfc-editor.org/rfc/rfc6749.html

This remains the foundational OAuth 2.0 specification for:

```text
Authorization Code Grant
Authorization Endpoint
Token Endpoint
Authorization Code
Client
Authorization Server
Access Token
```

PKCE is an extension to this foundational flow.

---

# 44. Source Currency / Update Check

The applicable standards were checked before drafting.

The current relationship is:

```text
RFC 6749
    │
    └── OAuth 2.0 Authorization Code foundation
            │
            ▼
RFC 7636
    │
    └── PKCE mechanism
            │
            ▼
RFC 9700
    │
    └── Current OAuth Security BCP
            │
            ├── PKCE required for public Clients
            ├── Authorization Servers MUST support PKCE
            ├── S256 preferred
            ├── PKCE downgrade protection
            ├── Authorization Code injection protection
            └── Transaction-specific challenges
            │
            ▼
RFC 10017
    │
    └── Current browser-based OAuth guidance
            │
            ├── Browser public Clients MUST use PKCE
            ├── Authorization Servers MUST enforce PKCE
            ├── Browser-specific threat model
            └── Malicious JavaScript considerations
```

The important conclusion is:

```text
PKCE should not be taught today as merely
an optional extension from RFC 7636.
```

The modern implementation model is:

```text
Authorization Code Grant
        +
PKCE
        +
S256
        +
Transaction-specific verifier
        +
Replay / injection protection
        +
Current browser security guidance
```

For this learning track, PKCE is therefore a core security control of the modern Authorization Code flow rather than an optional enhancement.
