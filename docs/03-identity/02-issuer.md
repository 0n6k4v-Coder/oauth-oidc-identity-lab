# Lecture 06 — OpenID Connect Issuer

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Identity Trust & Discovery
> **Prerequisite:** Understanding of OAuth 2.0 Authorization Code Flow, ID Tokens, and basic ID Token validation

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain what an OpenID Connect Issuer is.
* Explain why the Issuer is a security-critical identity of an OpenID Provider.
* Understand the relationship between the Issuer, Discovery metadata, and the ID Token `iss` Claim.
* Explain why the Issuer is a URL rather than simply a hostname.
* Understand why the Issuer may contain a path component.
* Explain how an OpenID Connect Client establishes its expected Issuer.
* Validate that Discovery metadata belongs to the expected Issuer.
* Validate that an ID Token was issued by the expected Issuer.
* Understand how Issuer identification helps defend against OAuth mix-up attacks.
* Distinguish the Issuer from authorization endpoints, token endpoints, and other URLs.
* Understand the relationship between OpenID Connect Discovery and OAuth Authorization Server Metadata.

---

# 2. The Problem the Issuer Solves

Consider an application that wants to use an OpenID Provider.

It needs to know:

```text
Who is the OpenID Provider?
```

and not merely:

```text
Where is the login page?
```

For example:

```text
Authorization Endpoint
https://login.example.com/authorize
```

does not by itself fully identify the authorization server.

An authorization server can expose multiple endpoints:

```text
Authorization Endpoint
        │
        ▼
https://login.example.com/authorize

Token Endpoint
        │
        ▼
https://login.example.com/token

UserInfo Endpoint
        │
        ▼
https://login.example.com/userinfo

JWKS
        │
        ▼
https://login.example.com/keys
```

The Client therefore needs a stable identifier representing the security authority behind these endpoints.

That identifier is the:

```text
Issuer Identifier
```

Conceptually:

```text
                 Issuer
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
 Authorization   Token       JWKS /
   Endpoint     Endpoint     Metadata
```

The Issuer acts as the identity anchor from which the Client establishes which authorization and identity infrastructure it trusts.

---

# 3. What Is an Issuer?

In OpenID Connect, the Issuer Identifier identifies the OpenID Provider.

It is represented as a URL using:

```text
https
```

and must not contain:

```text
query
fragment
```

For example:

```text
https://login.example.com
```

or:

```text
https://login.example.com/tenant-a
```

The second example is important.

The path can be part of the Issuer Identifier.

Therefore:

```text
https://example.com
```

and:

```text
https://example.com/tenant-a
```

are different Issuers.

OpenID Connect Discovery explicitly defines the `issuer` metadata value as the OP's Issuer Identifier and requires it to use HTTPS with no query or fragment components.

---

# 4. Issuer Is an Identity, Not an Endpoint

A common mistake is to think:

```text
Issuer
=
Authorization Endpoint
```

They are not the same thing.

For example:

```text
Issuer
https://login.example.com
```

may identify the provider, while:

```text
Authorization Endpoint
https://login.example.com/authorize

Token Endpoint
https://login.example.com/token

UserInfo Endpoint
https://login.example.com/userinfo
```

are individual endpoints operated under that Issuer.

The relationship is:

```text
Issuer
   │
   ├── Authorization Endpoint
   ├── Token Endpoint
   ├── UserInfo Endpoint
   ├── JWKS URI
   └── Other Metadata
```

Therefore:

```text
Issuer
    =
Identity of the security authority

Endpoint
    =
Location of a particular protocol operation
```

---

# 5. Why the Issuer Matters to an ID Token

The previous lecture introduced:

```json
{
  "iss": "https://login.example.com",
  "sub": "123456",
  "aud": "client-123",
  "exp": 1735689600
}
```

The `iss` Claim identifies the issuer of the ID Token.

The Client should already know which Issuer it expects.

The validation relationship is:

```text
Expected Issuer
       │
       │ compare
       ▼
ID Token iss
       │
       ├── Match ──► Continue
       │
       └── Mismatch ► Reject
```

OpenID Connect requires the Issuer Identifier used by the Client to match the `iss` Claim in ID Tokens issued by that Issuer.

Therefore:

```text
Expected Issuer
      =
ID Token iss
```

is one of the fundamental trust checks in OpenID Connect.

---

# 6. The Issuer Is Part of Identity

Recall the previous lecture's model:

```text
iss + sub
```

can identify an external OpenID Connect subject.

For example:

```text
Issuer A
https://idp-a.example

sub
12345
```

is not the same external identity as:

```text
Issuer B
https://idp-b.example

sub
12345
```

Conceptually:

```text
(https://idp-a.example, 12345)
              ≠
(https://idp-b.example, 12345)
```

This means the Issuer is not merely configuration metadata.

It is part of the security identity context.

A useful model is:

```text
Issuer
   +
Subject
   ↓
External Identity
```

---

# 7. Issuer and Discovery

An OpenID Connect Client needs information about the OpenID Provider.

OpenID Connect Discovery provides a standardized mechanism for obtaining this information.

Conceptually:

```text
Known Issuer
     │
     │ Discovery
     ▼
OpenID Provider Metadata
```

The metadata can contain information such as:

```text
issuer
authorization_endpoint
token_endpoint
userinfo_endpoint
jwks_uri
response_types_supported
subject_types_supported
id_token_signing_alg_values_supported
...
```

The Client can therefore start with:

```text
Issuer
```

and discover:

```text
How do I communicate with this provider?
```

OpenID Connect Discovery 1.0 incorporating errata set 2 defines this mechanism and the Provider Metadata document.

---

# 8. The Discovery Relationship

For a simple Issuer:

```text
Issuer
https://server.example.com
```

the OpenID Connect Discovery document is conventionally located at:

```text
https://server.example.com/.well-known/openid-configuration
```

The resulting document might contain:

```json
{
  "issuer": "https://server.example.com",
  "authorization_endpoint":
    "https://server.example.com/authorize",
  "token_endpoint":
    "https://server.example.com/token",
  "jwks_uri":
    "https://server.example.com/jwks"
}
```

The critical relationship is:

```text
Configured Issuer
        │
        ▼
/.well-known/openid-configuration
        │
        ▼
Metadata
        │
        ▼
metadata.issuer
```

The returned:

```text
metadata.issuer
```

must match the Issuer used to retrieve the configuration.

OpenID Connect Discovery explicitly requires this validation.

---

# 9. Discovery Is Not the Issuer

Do not confuse:

```text
Issuer
```

with:

```text
Discovery Document
```

They are different concepts.

```text
Issuer
https://server.example.com
       │
       │ determines
       ▼
Discovery Location
https://server.example.com/.well-known/openid-configuration
       │
       ▼
Provider Metadata
```

The Issuer is the identity.

The Discovery document is configuration describing that identity's services.

Therefore:

```text
Issuer
    ≠
Discovery Document
```

---

# 10. Metadata Must Confirm the Issuer

Suppose the Client expects:

```text
https://honest.example
```

It retrieves:

```text
https://honest.example/.well-known/openid-configuration
```

but receives:

```json
{
  "issuer": "https://attacker.example"
}
```

The Client must not simply accept the remaining metadata.

Conceptually:

```text
Expected Issuer
https://honest.example
        │
        │ compare
        ▼
metadata.issuer
https://attacker.example
        │
        ▼
       FAIL
        │
        ▼
Do not use metadata
```

OAuth Authorization Server Metadata defines the same fundamental validation principle: the returned `issuer` value must be identical to the issuer identifier used to derive the metadata location; otherwise the metadata must not be used.

---

# 11. Why Exact Matching Matters

Issuer comparison is security-sensitive.

Consider:

```text
https://example.com
```

and:

```text
https://example.com/tenant-a
```

They are not automatically interchangeable.

Similarly:

```text
https://example.com
```

and:

```text
https://example.com.evil.example
```

are completely different Issuers.

The Client should therefore not use vague comparisons such as:

```text
startsWith()
contains()
same hostname only
```

when the protocol requires an exact Issuer comparison.

The relevant specifications require exact identity relationships between the configured Issuer, discovered metadata, and ID Token `iss` Claim.

---

# 12. Issuer Paths Are Significant

An Issuer can contain a path.

For example:

```text
https://example.com/tenant-a
```

and:

```text
https://example.com/tenant-b
```

may represent different Issuers hosted by the same server.

Conceptually:

```text
                     example.com
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
       /tenant-a                /tenant-b
             │                       │
             ▼                       ▼
         Issuer A                 Issuer B
```

This is important for multi-tenant systems.

OpenID Connect explicitly supports multiple Issuers on the same host and treats the path component as part of the Issuer Identifier.

Therefore:

```text
https://example.com/tenant-a
```

must not be normalized into:

```text
https://example.com
```

when performing Issuer identity validation.

---

# 13. Issuer and OpenID Provider Metadata

The relationship can be summarized as:

```text
Issuer
   │
   │ identifies
   ▼
OpenID Provider
   │
   │ publishes
   ▼
Provider Metadata
   │
   ├── issuer
   ├── authorization_endpoint
   ├── token_endpoint
   ├── jwks_uri
   └── ...
```

The `issuer` metadata member is therefore not just descriptive text.

It confirms:

```text
"This metadata describes the provider identified by this Issuer."
```

The Client should establish this relationship before trusting the endpoints and keys discovered through the metadata.

---

# 14. Issuer and Signing Keys

The Issuer also establishes the trust context for signing keys.

Conceptually:

```text
Expected Issuer
       │
       ▼
Provider Metadata
       │
       ▼
jwks_uri
       │
       ▼
Trusted Signing Keys
       │
       ▼
ID Token Signature Validation
```

The Client should not reason:

```text
Token says:
kid = abc123

Therefore:
fetch any key associated with abc123
```

Instead:

```text
Expected Issuer
       │
       ▼
Trusted Provider Configuration
       │
       ▼
Trusted JWKS Location
       │
       ▼
Signing Key
       │
       ▼
Validate ID Token
```

This is one reason Issuer validation must happen as part of establishing the OpenID Provider trust relationship.

OpenID Connect Discovery's security considerations specifically warn against accepting metadata that falsely claims to belong to a trusted Issuer while pointing to attacker-controlled endpoints or signing keys.

---

# 15. Issuer → Metadata → ID Token

The most useful mental model is:

```text
                 TRUST CHAIN

Configured Issuer
       │
       ▼
Discovery Metadata
       │
       │ metadata.issuer
       ▼
Same Issuer
       │
       ▼
Provider Endpoints / Keys
       │
       ▼
ID Token
       │
       │ iss
       ▼
Same Issuer
```

The Client therefore wants:

```text
Configured Issuer
       =
Metadata issuer
       =
ID Token iss
```

When these relationships hold, the Client has a coherent identity context for the OpenID Provider.

---

# 16. What If the Issuer Does Not Match?

Suppose:

```text
Expected Issuer:
https://login.example.com
```

but:

```text
ID Token:
{
  "iss": "https://evil.example.com"
}
```

The Client must reject the ID Token.

Likewise, if:

```text
Expected Issuer
        ≠
Metadata issuer
```

the Client must not use the metadata.

The general rule is:

```text
Issuer mismatch
      ↓
Trust relationship failed
      ↓
Abort
```

This prevents the Client from accidentally treating another security authority as the expected OpenID Provider.

---

# 17. Issuer and OAuth Mix-Up Attacks

The Issuer becomes even more important when a Client supports multiple authorization servers.

Imagine:

```text
Client
 ├── Authorization Server A
 └── Authorization Server B
```

The Client begins an authorization request intended for:

```text
Authorization Server A
```

but receives a response associated with:

```text
Authorization Server B
```

If the Client cannot determine which authorization server produced the response, it may send credentials such as an authorization code to the wrong server.

This class of attack is known as:

```text
OAuth Mix-Up Attack
```

Current OAuth security guidance explicitly treats mix-up attacks as a security concern for clients interacting with multiple authorization servers.

---

# 18. Issuer as a Mix-Up Defense

Current OAuth Security BCP describes issuer identification as one defense against mix-up attacks.

The basic idea is:

```text
Authorization Request
        │
        │ sent to Issuer A
        ▼
   Issuer A
        │
        │ Authorization Response
        │ iss = Issuer A
        ▼
      Client
        │
        │ compare
        ▼
Stored Issuer A
```

If the response says:

```text
iss = Issuer B
```

while the request was sent to:

```text
Issuer A
```

the Client must abort the interaction.

RFC 9700 requires this kind of mix-up defense when a Client interacts with multiple authorization servers.

---

# 19. RFC 9207 — Authorization Response Issuer Identification

OAuth 2.0 historically did not include the authorization server's identity in the standard authorization response.

RFC 9207 defines an explicit:

```text
iss
```

authorization-response parameter.

For an authorization server supporting RFC 9207:

```text
Authorization Response
        │
        ├── code
        ├── state
        └── iss
```

For example:

```text
https://client.example/callback?
    code=AUTHORIZATION_CODE&
    state=STATE&
    iss=https%3A%2F%2Fhonest.example
```

The Client compares the returned `iss` to the expected Issuer.

If they do not match:

```text
Reject authorization response
```

RFC 9207 specifies this mechanism specifically to provide explicit authorization-server issuer identification and mitigate mix-up attacks.

---

# 20. OIDC `iss` vs OAuth Response `iss`

There can therefore be two related issuer-identification mechanisms.

### ID Token

```text
ID Token
{
  "iss": "https://issuer.example"
}
```

### OAuth Authorization Response

```text
/callback?
    code=...&
    iss=https%3A%2F%2Fissuer.example
```

They serve related security purposes but occur at different protocol locations.

RFC 9207 states that in OpenID Connect flows where an ID Token is returned from the authorization endpoint, the authorization-response `iss` value must be identical to the ID Token's `iss` Claim.

Current OAuth Security BCP also identifies these as mechanisms for issuer-based mix-up defense.

---

# 21. Issuer and `state`

Issuer validation does not replace all other transaction protections.

A modern OAuth Client may need protections involving:

```text
PKCE
state
nonce
issuer identification
redirect URI binding
```

These mechanisms address different aspects of the authorization transaction.

For example:

```text
PKCE
  ↓
Authorization Code binding

state
  ↓
Authorization response / CSRF protection

nonce
  ↓
OIDC authentication response binding

Issuer identification
  ↓
Authorization Server identity / mix-up defense
```

Current OAuth Security BCP describes these protections together as part of the modern OAuth security model.

---

# 22. Issuer Is Not the Same as Hostname

Consider:

```text
https://example.com/tenant-a
```

The hostname is:

```text
example.com
```

The Issuer is:

```text
https://example.com/tenant-a
```

Therefore:

```text
Hostname
    =
Network location component

Issuer
    =
Protocol-level security identifier
```

This distinction matters particularly in:

```text
Multi-tenant identity systems
Identity platforms
Federation systems
Shared hosting environments
```

Two Issuers can potentially exist under one host.

---

# 23. Issuer Is Not the Same as Tenant Name

Suppose a provider uses:

```text
tenant-a
```

as an internal tenant identifier.

That does not automatically mean:

```text
Issuer = tenant-a
```

The Issuer is a protocol-defined URL.

For example:

```text
Tenant
    tenant-a

Issuer
    https://login.example.com/tenant-a
```

The tenant may be represented by part of the Issuer URL, but the concepts should not be conflated.

---

# 24. Issuer and Multi-Tenancy

A multi-tenant identity platform can conceptually look like:

```text
                   Identity Platform
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        Tenant A                  Tenant B
              │                       │
              ▼                       ▼
https://id.example/a       https://id.example/b
              │                       │
              ▼                       ▼
          Issuer A                 Issuer B
```

The two Issuers can share:

```text
Host
```

while remaining distinct security authorities because the path is part of the Issuer Identifier.

This is why Issuer comparison must preserve the complete Issuer value.

---

# 25. OAuth Authorization Server Metadata vs OIDC Discovery

OpenID Connect Discovery and OAuth Authorization Server Metadata are closely related.

OAuth defines:

```text
RFC 8414
OAuth 2.0 Authorization Server Metadata
```

OpenID Connect defines:

```text
OpenID Connect Discovery
```

Both provide standardized metadata describing the authorization/identity server.

The conceptual model is:

```text
OAuth
  │
  ▼
Authorization Server Metadata
  │
  ├── issuer
  ├── authorization_endpoint
  ├── token_endpoint
  └── ...
```

and:

```text
OpenID Connect
  │
  ▼
OpenID Provider Metadata
  │
  ├── issuer
  ├── authorization_endpoint
  ├── token_endpoint
  ├── userinfo_endpoint
  ├── jwks_uri
  └── ...
```

OpenID Connect Discovery builds on the OAuth ecosystem and defines the additional information required for OpenID Connect.

---

# 26. The Issuer as the Trust Anchor

The complete relationship can now be represented as:

```text
                  TRUST ANCHOR

                 Expected Issuer
                       │
                       ▼
              Provider Metadata
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        Endpoints              JWKS
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                   ID Token
                       │
                       ▼
                 iss validation
                       │
                       ▼
                Trusted Identity
```

This is the most important concept in the lecture.

The Client should not start by trusting:

```text
Authorization Endpoint
Token Endpoint
JWKS URI
ID Token
```

independently.

Instead, it establishes:

```text
Which Issuer do I trust?
```

and then uses validated configuration associated with that Issuer.

---

# 27. A Complete Issuer Validation Flow

A simplified OpenID Connect Client process can be represented as:

```text
1. Determine expected Issuer.

2. Retrieve Provider Metadata.

3. Validate metadata.issuer.

4. Accept the provider configuration only if
   the Issuer relationship is valid.

5. Obtain trusted endpoint and key information.

6. Receive an ID Token.

7. Validate ID Token signature using trusted keys.

8. Validate ID Token iss.

9. Ensure the Issuer corresponds to the expected provider.

10. Continue with remaining ID Token validation.
```

Conceptually:

```text
Expected Issuer
       │
       ▼
Discovery
       │
       ▼
Validate Metadata Issuer
       │
       ▼
Trusted Configuration
       │
       ▼
Receive ID Token
       │
       ▼
Validate iss
       │
       ▼
Continue ID Token Validation
```

---

# 28. What the Client Must Not Do

Avoid these patterns.

### Mistake 1 — Trust the Token's Issuer

```text
Read:
iss = https://example.com

Therefore:
trust https://example.com
```

Wrong.

The expected Issuer must come from a trusted configuration or deployment context.

---

### Mistake 2 — Trust Metadata Without Checking `issuer`

```text
Fetch metadata
      ↓
Use endpoints immediately
```

Wrong.

The metadata must correspond to the expected Issuer.

---

### Mistake 3 — Compare Only Hostnames

```text
Expected:
https://example.com/tenant-a

Received:
https://example.com/tenant-b

Same hostname
      ↓
Accept
```

Wrong.

The Issuer Identifier includes the path.

---

### Mistake 4 — Treat Issuer as an Endpoint

```text
Issuer
=
Token Endpoint
```

Wrong.

The Issuer identifies the provider; endpoints perform specific operations.

---

### Mistake 5 — Ignore Issuer When Supporting Multiple Authorization Servers

```text
Authorization Server A
Authorization Server B

       ↓

Treat every response identically
```

Dangerous.

Current OAuth security guidance requires a mix-up defense when a Client interacts with multiple authorization servers.

---

# 29. Security Mental Model

The safest mental model is:

```text
                "WHO?"

                 Issuer
                   │
                   ▼
          Which security authority?
                   │
                   ▼
             Metadata
                   │
                   ▼
          Which endpoints/keys?
                   │
                   ▼
              ID Token
                   │
                   ▼
              iss Claim
                   │
                   ▼
          Does it match?
                   │
              ┌────┴────┐
              │         │
             Yes        No
              │         │
              ▼         ▼
          Continue     Reject
```

The Issuer answers the fundamental trust question:

```text
Who is this authentication authority?
```

---

# 30. Knowledge Check

### Question 1

What is an OpenID Connect Issuer?

---

### Question 2

Why is the Issuer different from the Authorization Endpoint?

---

### Question 3

What restrictions apply to an OpenID Connect Issuer Identifier?

---

### Question 4

Why can two Issuers on the same hostname still be different?

---

### Question 5

What relationship should exist between:

```text
Configured Issuer
Metadata issuer
ID Token iss
```

---

### Question 6

Why must the Client validate the `issuer` value returned in Provider Metadata?

---

### Question 7

What could happen if a Client accepts metadata that claims to belong to a trusted Issuer but contains attacker-controlled endpoints or keys?

---

### Question 8

What is an OAuth mix-up attack?

---

### Question 9

How does Issuer identification help defend against mix-up attacks?

---

### Question 10

What does RFC 9207 add to OAuth authorization responses?

---

### Question 11

Why is hostname-only comparison insufficient for Issuer validation?

---

### Question 12

Explain the relationship between:

```text
Issuer
Discovery
Metadata
JWKS
ID Token
```

in one coherent explanation.

---

# 31. Lecture Summary

The Issuer is the identity anchor of an OpenID Provider.

It is not merely:

```text
A hostname
```

or:

```text
An endpoint URL
```

Instead:

```text
Issuer
   =
Identity of the OpenID Provider
```

The Client establishes a trusted Issuer and uses it to validate the provider's configuration.

The essential relationship is:

```text
Expected Issuer
      =
Metadata issuer
      =
ID Token iss
```

The Issuer also becomes important when a Client interacts with multiple authorization servers.

Modern OAuth security guidance requires defenses against mix-up attacks in that scenario, and issuer identification is one of the standardized defenses. RFC 9207 defines the authorization-response `iss` parameter for this purpose.

The core mental model is:

```text
Issuer
   ↓
Provider Identity
   ↓
Trusted Metadata
   ↓
Trusted Endpoints / Keys
   ↓
ID Token
   ↓
iss Validation
   ↓
Trusted Identity Context
```

The most important distinction to retain is:

```text
Endpoint
    =
Where a protocol operation happens

Issuer
    =
Which security authority the Client is interacting with
```

---

# 32. References

## 32.1 OpenID Connect Discovery 1.0 incorporating errata set 2

**Authority:** OpenID Foundation

**Current applicable specification used for this lecture:** Final specification incorporating Errata Set 2, published December 15, 2023.

Official source:

https://openid.net/specs/openid-connect-discovery-1_0.html

Relevant topics:

```text
Section 2
OpenID Provider Issuer Discovery

Section 3
OpenID Provider Metadata

Section 4
Obtaining OpenID Provider Configuration Information

Section 4.3
OpenID Provider Configuration Validation

Section 7
Security Considerations
```

This is the primary OpenID Connect source for the Issuer and Discovery concepts. It defines the `issuer` metadata value, its relationship to the Issuer Identifier, Discovery, and ID Token `iss`.

---

## 32.2 RFC 8414 — OAuth 2.0 Authorization Server Metadata

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Standards Track.

Official source:

https://www.rfc-editor.org/rfc/rfc8414.html

Relevant topics:

```text
Section 2
Authorization Server Metadata

Section 3
Obtaining Authorization Server Metadata

Section 3.3
Authorization Server Metadata Validation

Section 4
String Operations
```

RFC 8414 defines the OAuth Authorization Server Metadata `issuer` value and requires the returned issuer to match the issuer used to obtain the metadata.

---

## 32.3 RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Best Current Practice (BCP 240).

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

Relevant topics:

```text
Section 4.4
Mix-Up Attacks

Section 4.4.2
Countermeasures

Section 4.4.2.1
Mix-Up Defense via Issuer Identification

Section 4.4.2.2
Mix-Up Defense via Distinct Redirect URIs
```

RFC 9700 is the current OAuth Security BCP used to update the security interpretation of the older OAuth framework. It requires Clients interacting with multiple authorization servers to prevent mix-up attacks and describes issuer identification as a defense.

---

## 32.4 RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification

**Authority:** Internet Engineering Task Force (IETF)

**Status:** Standards Track.

Official source:

https://www.rfc-editor.org/rfc/rfc9207.html

Relevant topics:

```text
Section 2
Response Parameter iss

Section 2.3
Providing the Issuer Identifier

Section 2.4
Validating the Issuer Identifier

Section 3
Authorization Server Metadata

Section 4
Security Considerations
```

RFC 9207 defines the authorization-response `iss` parameter and specifies how Clients compare it with the expected Issuer to defend against mix-up attacks.

---

## 32.5 Source Currency / Update Check

The relevant sources were checked for newer applicable specifications before drafting.

```text
OpenID Connect Discovery 1.0
        │
        └── Current published form:
            incorporating Errata Set 2
            (2023)

OAuth Authorization Server Metadata
        │
        └── RFC 8414
            Foundational metadata specification

OAuth Security
        │
        └── RFC 9700
            BCP 240
            Current OAuth Security BCP
            updates and extends earlier OAuth
            security guidance

Authorization Server Issuer Identification
        │
        └── RFC 9207
            Explicit authorization-response
            issuer identification
```

Therefore this lecture does not rely solely on the older OAuth 2.0 specifications for Issuer security.

The applicable model is:

```text
OpenID Connect Discovery
        +
OAuth Authorization Server Metadata
        +
RFC 9207
        +
RFC 9700
        ↓
Modern Issuer Identity & Trust Model
```

The older OAuth specifications remain relevant as foundational protocol specifications, but the security interpretation in this lecture follows the newer applicable standards and Best Current Practice.
