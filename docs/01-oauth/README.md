# OAuth 2.0 Theory

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Unit:** 01 — OAuth 2.0  
> **Scope:** Provider-neutral OAuth 2.0 protocol theory and security foundations

This unit builds the conceptual and protocol foundation required to understand, implement, test, and later deploy OAuth 2.0 and OpenID Connect systems.

The material is intentionally **provider-neutral**. Products such as Microsoft Entra ID, Auth0, Keycloak, or other Authorization Server implementations may be introduced later as concrete implementations of the concepts established here.

---

## 1. What This Unit Teaches

This unit follows one continuous OAuth authorization transaction rather than treating OAuth as a collection of unrelated terms.

The learning path is:

```text
OAuth Model
    ↓
OAuth Roles
    ↓
Authorization Request
    ↓
Authorization Code
    ↓
Token Exchange
    ↓
Access Token
    ↓
Refresh Token
    ↓
PKCE
```

The learner should progressively move from:

```text
What is OAuth?
```

to:

```text
Who participates?
```

then:

```text
How does authorization begin?
```

then:

```text
How is the authorization result represented?
```

then:

```text
How is it exchanged for tokens?
```

and finally:

```text
How are those credentials secured throughout their lifecycle?
```

---

## 2. Unit Learning Objectives

After completing this unit, you should be able to:

* Explain OAuth 2.0 as an authorization framework rather than a login protocol.
* Identify the four primary OAuth roles and their responsibilities.
* Trace an Authorization Code transaction from authorization request through protected-resource access.
* Explain the purpose of the Authorization Endpoint and Token Endpoint.
* Distinguish an authorization grant, Authorization Code, Access Token, and Refresh Token.
* Explain how authorization requests establish transaction context.
* Explain how authorization codes are redeemed securely.
* Explain Access Token scope, audience/resource targeting, lifetime, and presentation.
* Compare opaque and structured Access Tokens at a conceptual level.
* Explain Refresh Token lifecycle, rotation, revocation, and replay protection.
* Explain PKCE and its role in Authorization Code security.
* Distinguish PKCE, `state`, and Client authentication.
* Recognize common OAuth threats and the controls used to mitigate them.
* Interpret OAuth 2.0 using current security and deployment guidance rather than relying on historical RFC 6749 behavior alone.
* Connect protocol theory to the implementation Labs in this repository.

---

# 3. Lecture Map

| Lecture | Topic | Main Question | Builds On |
|---|---|---|---|
| [01 — OAuth 2.0 Overview](./01-overview.md) | OAuth foundation | What problem does OAuth solve? | HTTP / client-server basics |
| [02 — OAuth 2.0 Roles](./02-roles.md) | Protocol roles | Who participates and who is responsible for what? | Lecture 01 |
| [03 — Authorization Request](./03-authorization-request.md) | Authorization initiation | How does a Client start authorization? | Lectures 01–02 |
| [04 — Authorization Code](./04-authorization-code.md) | Authorization grant | What is the code and why is it temporary? | Lecture 03 |
| [05 — Token Exchange](./05-token-exchange.md) | Token issuance | How does a Client redeem the code? | Lectures 03–04 |
| [06 — Access Token](./06-access-token.md) | Resource authorization | What does the resulting token authorize? | Lecture 05 |
| [07 — Refresh Token](./07-refresh-token.md) | Token lifecycle | How can authorization continue after Access Token expiry? | Lectures 05–06 |
| [08 — PKCE](./08-pkce.md) | Code-flow security | How is the authorization transaction bound to the redeeming Client? | Lectures 03–05 |

The order is deliberate. PKCE is taught last in this unit even though it first appears in earlier lectures because its full value becomes easier to understand after the Authorization Request, Authorization Code, and Token Exchange are already familiar.

---

# 4. The Learning Spine

The entire unit can be reduced to one continuous protocol story:

```text
Resource Owner
      │
      │ authorization
      ▼
Authorization Server
      │
      │ authorization response
      │
      ▼
Client
      │
      │ Authorization Code
      ▼
Token Endpoint
      │
      │ validation
      │
      ▼
Access Token
      │
      │ protected-resource request
      ▼
Resource Server
      │
      ▼
Protected Resource
```

The token lifecycle then extends the story:

```text
Access Token expires
        ↓
Refresh Token
        ↓
Token Endpoint
        ↓
New Access Token
```

PKCE adds a security binding across the Authorization Code transaction:

```text
code_verifier
      ↓
S256
      ↓
code_challenge
      ↓
Authorization Request
      ↓
Authorization Code
      ↓
Token Request + code_verifier
      ↓
Verification
```

This is the central protocol narrative for Unit 01.

---

# 5. How the Lectures Connect

## Lecture 01 → Lecture 02

Lecture 01 establishes the OAuth model and introduces the four roles.

Lecture 02 takes those roles and turns them into a responsibility model:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

Without this distinction, later protocol messages are difficult to place correctly.

## Lecture 02 → Lecture 03

Once the roles are clear, Lecture 03 asks:

```text
How does the Client actually begin authorization?
```

That leads to the Authorization Request and its protocol parameters.

## Lecture 03 → Lecture 04

Lecture 03 explains the request.

Lecture 04 explains the important result of an Authorization Code request:

```text
Authorization Code
```

The code becomes the authorization grant that the Client can later redeem.

## Lecture 04 → Lecture 05

Lecture 04 stops when the Client has the Authorization Code.

Lecture 05 continues the same transaction at the Token Endpoint:

```text
Authorization Code
        ↓
Token Request
        ↓
Validation
        ↓
Token Response
```

## Lecture 05 → Lecture 06

Lecture 05 ends with token issuance.

Lecture 06 asks what happens next:

```text
Who uses the Access Token?
```

The answer moves the focus from the Authorization Server to the Resource Server.

## Lecture 06 → Lecture 07

Lecture 06 establishes the Access Token lifecycle.

Lecture 07 extends that lifecycle when an Access Token expires:

```text
Access Token
      ↓
Refresh Token
      ↓
New Access Token
```

This introduces long-lived credentials, rotation, revocation, and replay protection.

## Lectures 03–05 → Lecture 08

PKCE appears earlier as an architectural requirement, but Lecture 08 isolates the mechanism and explains it in depth:

```text
code_verifier
      ↓
code_challenge
      ↓
Authorization Code
      ↓
code_verifier
      ↓
Token Endpoint validation
```

This allows PKCE to be understood as a security mechanism spanning multiple protocol stages rather than as one isolated parameter.

---

# 6. What You Should Know Before Starting

You should be comfortable with:

```text
HTTP requests and responses
URLs and query parameters
HTTP headers
Client-server communication
Basic browser behavior
Basic JSON
Basic application architecture
```

You do not need prior OAuth implementation experience.

The lectures introduce the OAuth-specific vocabulary progressively.

---

# 7. What This Unit Does Not Try to Teach

This unit establishes OAuth 2.0 fundamentals and security reasoning. It is not intended to be a complete reference for every OAuth extension or deployment architecture.

Topics outside the primary scope of this unit include:

```text
OpenID Connect Core identity semantics
Provider-specific configuration
Advanced federation
Enterprise identity administration
Every OAuth extension
Every token format implementation
Production key-management architecture
```

Those topics can build on this foundation later.

The important boundary is:

```text
Unit 01
    ↓
Understand OAuth 2.0 protocol behavior and security
    ↓
Later units
    ↓
Identity, providers, federation, and advanced deployment
```

---

# 8. Core Vocabulary

| Term | Meaning in This Unit |
|---|---|
| Resource Owner | Entity capable of granting access to a protected resource |
| Client | Application requesting access to a protected resource |
| Authorization Server | Server that processes authorization and issues tokens |
| Resource Server | Server protecting the resource |
| Authorization Endpoint | Endpoint used to initiate the authorization interaction |
| Token Endpoint | Endpoint used to obtain tokens from an authorization grant |
| Authorization Grant | Credential/representation used to obtain an Access Token |
| Authorization Code | Temporary authorization grant used in the Authorization Code flow |
| Access Token | Credential used to access protected resources |
| Refresh Token | Credential used to obtain new Access Tokens |
| Scope | Authorization scope associated with the request/token |
| Redirect URI | Destination to which the authorization response is returned |
| `state` | Client-controlled value used to correlate the authorization transaction and support CSRF defenses where applicable |
| PKCE | Proof mechanism binding the authorization request to the token request |
| `code_verifier` | High-entropy transaction secret generated by the Client |
| `code_challenge` | Derived value sent in the authorization request |

---

# 9. Security Model Used Throughout the Unit

The unit intentionally teaches OAuth as a security-sensitive protocol, not merely as a sequence of successful HTTP calls.

A working request is not automatically a secure request.

The recurring security questions are:

```text
Who is acting?
What is being requested?
Where is the response going?
What credential is being presented?
What transaction does the credential belong to?
What resource is the credential intended for?
Can the credential be replayed?
What happens if the credential leaks?
What happens if the Client is compromised?
```

The lectures repeatedly apply controls such as:

```text
Exact Redirect URI Handling
PKCE
CSRF / Transaction Correlation
Authorization-Code Protection
Client Authentication
Audience / Resource Restriction
Token Lifetime
Refresh Token Replay Detection
Sender-Constrained Tokens
Secure Transport
Secure Credential Handling
```

These controls should be understood as layers.

```text
Protocol correctness
      +
Transaction binding
      +
Credential protection
      +
Replay resistance
      +
Resource authorization
      +
Client / browser security
      ↓
Modern OAuth Security
```

---

# 10. Current Standards Model

OAuth 2.0 should not be studied as a single isolated document.

For this unit, the standards relationship is better represented as:

```text
RFC 6749
    ↓
OAuth 2.0 foundation
    │
    ├── roles
    ├── authorization grant model
    ├── endpoints
    ├── Access Tokens
    └── Refresh Tokens

RFC 7636
    ↓
PKCE mechanism

RFC 6750
    ↓
Bearer Token usage

RFC 7009
    ↓
Token revocation

RFC 7662
    ↓
Token introspection

RFC 8252
    ↓
Native application guidance

RFC 8705
    ↓
Mutual-TLS / certificate-bound tokens

RFC 8707
    ↓
Resource Indicators

RFC 9068
    ↓
JWT Access Token Profile

RFC 9207
    ↓
Authorization Server Issuer Identification

RFC 9449
    ↓
DPoP / sender-constrained tokens

RFC 9700
    ↓
Current OAuth 2.0 Security Best Current Practice
```

The lectures use these sources according to subject matter rather than treating every RFC as equally relevant to every topic.

The important principle is:

```text
Foundation
    ≠
Complete current security guidance
```

The foundational OAuth 2.0 model remains useful, while current security and deployment guidance must be applied where relevant.

---

# 11. Standards Update Principle

The material in this unit follows a source-currency rule:

```text
Before teaching a protocol behavior:

1. Identify the original specification.
2. Check for updates, obsoletes, replacements,
   supplements, and current Best Current Practice.
3. Determine whether the newer source changes
   the interpretation of the topic.
4. Incorporate the relevant change into the lecture.
5. Preserve historical context only when it improves understanding.
```

This prevents the learning material from accidentally teaching historical behavior as though it were the current recommended deployment model.

For example:

```text
RFC 6749
    ↓
Original OAuth 2.0 framework

RFC 9700
    ↓
Current OAuth security guidance
    ↓
Changes how several RFC 6749-era flows
should be implemented today
```

The lectures therefore distinguish between:

```text
What OAuth originally specified
```

and:

```text
How OAuth should be implemented today
```

when that distinction matters to the learning objective.

---

# 12. Provider-Neutral by Design

This unit intentionally avoids defining OAuth through a product.

For example, the following are conceptually different:

```text
OAuth concept
    ↓
Authorization Code
```

and:

```text
Provider implementation
    ↓
Microsoft Entra ID authorization code implementation
```

The correct learning direction is:

```text
Standard
    ↓
Protocol behavior
    ↓
Security properties
    ↓
Provider implementation
```

This makes it possible to transfer the knowledge to different Authorization Servers and deployment environments.

---

# 13. From Theory to Lab

The Labs associated with this unit are not intended to replace the lectures.

They are intended to make the protocol observable.

The basic learning loop is:

```text
Lecture
  ↓
Understand protocol concept
  ↓
Implement a small piece
  ↓
Run the system
  ↓
Inspect HTTP behavior
  ↓
Test success and failure cases
  ↓
Record the result
  ↓
Return to the protocol model
```

A Lab should therefore answer questions such as:

```text
What request was sent?
What response was returned?
Which component sent it?
Which component validated it?
Which security property was demonstrated?
What happened when the property was violated?
```

---

# 14. Lab Architecture Direction

The practical architecture for this learning track follows the same logical roles introduced in the lectures.

A simplified deployment can look like:

```text
                    ┌──────────────────────┐
                    │ Authorization Server │
                    └──────────┬───────────┘
                               │
                     Authorization Code
                               │
                               ▼
                    ┌──────────────────────┐
                    │   React OAuth Client │
                    └──────────┬───────────┘
                               │
                         Access Token
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Resource Server    │
                    │       FastAPI        │
                    └──────────────────────┘
```

The actual Lab architecture may evolve as later units introduce real Authorization Server and provider integrations.

The important point is that the implementation should preserve the protocol-role model established in Lectures 01–02.

---

# 15. Recommended Study Sequence

The recommended sequence is:

```text
Step 1
Read Lecture 01

Step 2
Read Lecture 02

Step 3
Read Lecture 03

Step 4
Read Lecture 04

Step 5
Read Lecture 05

Step 6
Read Lecture 06

Step 7
Read Lecture 07

Step 8
Read Lecture 08

Step 9
Complete the corresponding Labs

Step 10
Compare observed behavior with the standards model
```

Do not skip directly to implementation details if the protocol roles and transaction flow are still unclear.

The later security material depends on the earlier mental model.

---

# 16. Suggested Study Method

For each lecture, use four passes:

### Pass 1 — Protocol Story

Ask:

```text
Who is talking to whom?
What is being requested?
What credential is moving?
```

### Pass 2 — Security Boundary

Ask:

```text
What can an attacker steal?
What can an attacker modify?
What is bound to what?
```

### Pass 3 — Standards

Ask:

```text
Which RFC defines this behavior?
Which newer RFC changes its security interpretation?
```

### Pass 4 — Lab

Ask:

```text
Can I observe this behavior in the implementation?
Can I trigger the failure case?
Can I explain why the server accepted or rejected it?
```

This is the intended learning loop for the repository.

---

# 17. Security Questions You Should Eventually Be Able to Answer

By the end of this unit, you should be able to reason through questions such as:

```text
Why is OAuth different from authentication?

Why are the Authorization Server and Resource Server
separate protocol roles?

Why is the Authorization Code different from an Access Token?

Why is the Authorization Code short-lived and single-use?

Why is redirect_uri security-critical?

Why does PKCE use a verifier and a challenge?

Why is S256 preferred?

Why is a Bearer Token dangerous when leaked?

Why does an Access Token need an audience/resource boundary?

Why is a Refresh Token more sensitive than a short-lived
Access Token?

Why does Refresh Token rotation detect replay?

Why does sender-constraining change the attack requirement?

Why does sender-constraining not provide absolute security?

Why does browser-based OAuth need deployment-specific guidance?
```

These questions are more important than memorizing isolated parameters.

---

# 18. Common Misconceptions This Unit Is Designed to Correct

The lectures deliberately challenge several shortcuts:

```text
OAuth = Login
```

```text
Access Token = JWT
```

```text
Authorization Code = Access Token
```

```text
Client = Resource Owner
```

```text
Authorization Server = Resource Server
```

```text
PKCE = Client Authentication
```

```text
state = PKCE
```

```text
Refresh Token = Long-Lived Access Token
```

```text
Sender Constraint = 100% Security
```

```text
Working OAuth Flow = Secure OAuth Flow
```

The goal is to replace these shortcuts with protocol and threat-model reasoning.

---

# 19. Historical Context vs Modern Practice

Some OAuth behavior is best understood in historical context.

For example:

```text
Historical OAuth
    ↓
Implicit Grant
```

may appear in older systems or documentation.

Modern security guidance substantially changes the recommended approach:

```text
Modern OAuth
    ↓
Authorization Code
        +
PKCE where applicable / required
```

Similarly, the original OAuth 2.0 framework permits implementation choices that current security guidance may now constrain or discourage.

The purpose of this unit is therefore not to erase the history of OAuth, but to teach the historical specification and the modern security interpretation together where necessary.

---

# 20. Unit Completion Criteria

You have completed the theory unit when you can explain the following sequence without referring to notes:

```text
Resource Owner
      ↓
Client
      ↓
Authorization Request
      ↓
Authorization Server
      ↓
Authorization Code
      ↓
Token Endpoint
      ↓
Access Token
      ↓
Resource Server
      ↓
Protected Resource
```

and extend it with:

```text
Access Token expires
      ↓
Refresh Token
      ↓
Token Endpoint
      ↓
New Access Token
```

and explain the PKCE security binding:

```text
Client
  │
  │ code_verifier
  ▼
S256
  │
  ▼
code_challenge
  │
  ▼
Authorization Request
  │
  ▼
Authorization Code
  │
  ▼
Token Request
  │
  │ code_verifier
  ▼
PKCE verification
```

You should also be able to identify where each major security control is applied.

---

# 21. Unit Summary

Unit 01 builds the foundation for the remainder of the repository.

OAuth 2.0 is taught as an authorization framework with four primary roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The primary Authorization Code journey is:

```text
Authorization Request
        ↓
Authorization Code
        ↓
Token Exchange
        ↓
Access Token
        ↓
Protected Resource
```

The lifecycle then extends with:

```text
Refresh Token
        ↓
New Access Token
```

The modern security layer adds:

```text
PKCE
Exact Redirect URI Handling
CSRF / Transaction Binding
Authorization-Code Protection
Token Audience / Resource Restriction
Replay Protection
Token Lifetime
Revocation
Sender-Constrained Tokens where appropriate
Secure Client / Browser Architecture
```

The central principle of the unit is:

```text
OAuth is not just a token flow.

It is a protocol involving:

Roles
Transactions
Credentials
Trust Boundaries
Authorization Decisions
Security Controls
```

Understanding these relationships is the prerequisite for studying OpenID Connect, real Authorization Server products, federation, and more advanced identity architectures.

---

# 22. Standards and Source Fence

> The following sources form the standards basis for Unit 01. The list is intentionally scoped to sources that materially inform the lectures in this unit.

```text
CORE OAUTH 2.0 FOUNDATION

RFC 6749
The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Provides the foundational OAuth 2.0 model:
- Resource Owner
- Client
- Authorization Server
- Resource Server
- Authorization Grant
- Authorization Code Grant
- Authorization Endpoint
- Token Endpoint
- Access Token
- Refresh Token
- Scope


CURRENT OAUTH SECURITY BASELINE

RFC 9700
Best Current Practice for OAuth 2.0 Security
BCP 240
https://www.rfc-editor.org/rfc/rfc9700.html

Current general OAuth 2.0 security guidance used throughout
this unit where applicable.

Relevant themes include:
- Authorization Code security
- PKCE
- Redirect URI protection
- CSRF protection
- Authorization Code injection
- Mix-up attack mitigation
- Access Token protection
- Refresh Token protection
- Replay resistance
- Sender-constrained tokens
- Secure modern OAuth deployments


PKCE

RFC 7636
Proof Key for Code Exchange by OAuth Public Clients
https://www.rfc-editor.org/rfc/rfc7636.html

Defines:
- code_verifier
- code_challenge
- code_challenge_method
- PKCE protocol flow


BEARER TOKENS

RFC 6750
OAuth 2.0 Bearer Token Usage
https://www.rfc-editor.org/rfc/rfc6750.html

Defines bearer-token presentation and related security considerations.


TOKEN REVOCATION

RFC 7009
OAuth 2.0 Token Revocation
https://www.rfc-editor.org/rfc/rfc7009.html

Defines the token revocation mechanism used in the Refresh Token lifecycle.


TOKEN INTROSPECTION

RFC 7662
OAuth 2.0 Token Introspection
https://www.rfc-editor.org/rfc/rfc7662.html

Defines the introspection model for Resource Servers that need
current token state and metadata from an Authorization Server.


NATIVE APPLICATIONS

RFC 8252
OAuth 2.0 for Native Apps
https://www.rfc-editor.org/rfc/rfc8252.html

Provides deployment-specific guidance for native OAuth Clients,
including external user-agent use and PKCE.


MUTUAL-TLS

RFC 8705
OAuth 2.0 Mutual-TLS Client Authentication and
Certificate-Bound Access Tokens
https://www.rfc-editor.org/rfc/rfc8705.html

Defines mutual-TLS client authentication and certificate-bound
tokens for sender-constrained deployments.


RESOURCE INDICATORS

RFC 8707
Resource Indicators for OAuth 2.0
https://www.rfc-editor.org/rfc/rfc8707.html

Defines the resource parameter for explicitly targeting a protected resource.


JWT ACCESS TOKENS

RFC 9068
JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens
https://www.rfc-editor.org/rfc/rfc9068.html

Defines a standardized profile for JWT-formatted OAuth Access Tokens.


AUTHORIZATION SERVER ISSUER IDENTIFICATION

RFC 9207
OAuth 2.0 Authorization Server Issuer Identification
https://www.rfc-editor.org/rfc/rfc9207.html

Defines authorization-response issuer identification used to help
mitigate OAuth mix-up attacks.


DPoP

RFC 9449
OAuth 2.0 Demonstrating Proof of Possession
https://www.rfc-editor.org/rfc/rfc9449.html

Defines DPoP and sender-constrained Access / Refresh Token mechanisms.


BROWSER-BASED APPLICATIONS

RFC 10017
OAuth 2.0 for Browser-Based Applications
https://www.rfc-editor.org/rfc/rfc10017.html

Provides deployment-specific guidance for browser-based OAuth Clients,
including browser threat models and modern token-handling architectures.
```

---

# 23. Source Update Analysis

The unit follows the principle that newer applicable specifications are integrated into the lectures rather than being mentioned only in a reference list.

The standards relationship can be summarized as:

```text
RFC 6749
    ↓
Foundation
    │
    ├── Roles
    ├── Grants
    ├── Endpoints
    ├── Authorization Code
    ├── Access Token
    └── Refresh Token

RFC 7636
    ↓
PKCE mechanism

RFC 6750
    ↓
Bearer Token usage

RFC 7009
    ↓
Revocation

RFC 7662
    ↓
Introspection

RFC 8252
    ↓
Native-app deployment guidance

RFC 8705
    ↓
Certificate-bound tokens / mTLS

RFC 8707
    ↓
Resource targeting

RFC 9068
    ↓
JWT Access Token profile

RFC 9207
    ↓
Issuer identification

RFC 9449
    ↓
DPoP / sender constraint

RFC 9700
    ↓
Current OAuth security baseline

RFC 10017
    ↓
Browser-specific deployment guidance
```

The important teaching rule is:

```text
Older specification
    ↓
Historical / foundational behavior

Current specification or BCP
    ↓
Current security interpretation

Lecture
    ↓
Both are taught together when necessary
```

This avoids two common problems:

```text
Problem 1:
Teaching only the original RFC
and accidentally presenting outdated security practice.

Problem 2:
Teaching only modern recommendations
without understanding the protocol model they refine.
```

---

# 24. Repository Navigation

The structure for this unit is intentionally simple:

```text
docs/
└── 01-oauth/
    ├── README.md
    ├── 01-overview.md
    ├── 02-roles.md
    ├── 03-authorization-request.md
    ├── 04-authorization-code.md
    ├── 05-token-exchange.md
    ├── 06-access-token.md
    ├── 07-refresh-token.md
    └── 08-pkce.md
```

Use `README.md` as the map of the unit.

Use the numbered lecture files for the actual teaching material.

Use the corresponding Lab directories to move from theory to implementation and observation.

---

# 25. Final Mental Model

```text
                   OAUTH 2.0
                       │
                       ▼
              Delegated Authorization
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     Roles         Transaction      Credentials
        │              │              │
        │              │        ┌─────┼─────┐
        │              │        │     │     │
        │              │       Code  AT     RT
        │              │                  
        │              │
        └──────────────┼──────────────┘
                       ▼
                Security Controls
                       │
        ┌──────────────┼──────────────┐
        │              │              │
       PKCE       Redirect URI     Replay
        │              │           Protection
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Protected Resource
```

The unit should leave you with one durable idea:

```text
OAuth 2.0 is a framework for delegated authorization,
implemented through protocol roles, authorization transactions,
credentials, and security controls.
```

Everything in later identity and provider-specific units builds on this model.
