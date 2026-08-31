# OpenID Connect ID Token

The **ID Token** is the primary identity artifact defined by OpenID Connect. It is a security token that contains Claims about the authentication of an End-User by an OpenID Provider (OP), and potentially other requested Claims. In OpenID Connect Core, the ID Token is represented as a **JSON Web Token (JWT)**. citeturn1search0turn0search5

This lecture focuses on what an ID Token is, what information it carries, how it is structured, and what an OpenID Connect Client (Relying Party) must establish before trusting it.

## 1. Why the ID Token Exists

OAuth 2.0 provides an authorization framework. It does not define a standardized token whose purpose is to tell a Client which End-User was authenticated and what authentication event occurred.

OpenID Connect adds that identity layer.

```text
OAuth 2.0
    │
    │ authorization
    ▼
Authorization Server

OpenID Connect
    │
    │ authentication + identity
    ▼
OpenID Provider
    │
    │
    ▼
ID Token
```

The ID Token is therefore not simply an Access Token with a different name. Its purpose is to communicate the result of authentication and identity-related information to the Client. citeturn1search0

## 2. ID Token as a JWT

OpenID Connect Core defines the ID Token as a JWT.

A JWT is a compact, URL-safe representation of claims. The JWT format itself is defined by RFC 7519, while RFC 8725 provides current Best Current Practice for secure JWT implementation and deployment. citeturn0search5turn0search3

Conceptually:

```text
ID Token
   │
   └── JWT
        │
        ├── JOSE Header
        ├── JWT Claims Set
        └── Signature
```

For the normal signed ID Token, the important conceptual distinction is that the Client does not trust the JSON merely because it can decode it. The token's cryptographic protection and Claims must be validated before the identity information is trusted.

## 3. The JOSE Header

The first part of a JWT is its JOSE Header.

For an ID Token, the header identifies the cryptographic algorithm used to protect the token. OpenID Connect requires ID Tokens to be signed using JWS. An ID Token may additionally be encrypted using JWE; when encryption is used, the ID Token is signed first and then encrypted. citeturn1search0

A simplified header might look like:

```json
{
  "alg": "RS256",
  "kid": "key-1"
}
```

The `alg` value is security-relevant. RFC 8725 requires applications and JWT libraries to restrict accepted algorithms rather than blindly accepting whatever algorithm a token declares. citeturn0search3

The `kid` value can identify the key used for verification when the OP publishes multiple signing keys. How the Client discovers those keys belongs to the Discovery and signing-key portions of the learning path.

## 4. The JWT Claims Set

The second part of the JWT is the JWT Claims Set.

OpenID Connect defines Claims that allow the Client to understand the issuer, the intended audience, the End-User identifier, and important timing and authentication information.

A representative ID Token can contain:

```json
{
  "iss": "https://server.example.com",
  "sub": "24400320",
  "aud": "client-123",
  "exp": 1710003600,
  "iat": 1710000000,
  "nonce": "transaction-specific-value",
  "auth_time": 1710000000,
  "acr": "urn:example:loa:2"
}
```

This is an illustrative example rather than a universal set of Claims. The exact Claims present depend on the flow, request, registration, and authentication context. citeturn1search0

## 5. The Core Identity Claims

Several Claims are fundamental to understanding an ID Token.

### `iss` — Issuer

`iss` identifies the issuer of the ID Token.

The Client must establish that the token was issued by the expected OpenID Provider. The issuer is therefore part of the token's security context, not merely descriptive profile information.

JWT Best Current Practice also requires applications to ensure that the cryptographic keys used for a JWT belong to the issuer identified by the `iss` Claim when such a Claim is present. citeturn0search3

### `sub` — Subject

`sub` identifies the End-User at the issuer.

OpenID Connect defines it as a locally unique and never reassigned identifier within the Issuer for the Client, which makes it the stable identifier that an RP should use when associating the authentication result with an account. citeturn1search0

The RP should not treat human-readable profile attributes such as an email address as a substitute for the protocol-defined subject identifier.

### `aud` — Audience

`aud` identifies the intended audience of the ID Token.

For an ID Token issued to a Client, the Client's `client_id` must be present as an audience. The Claim may be either a single string or an array of strings depending on the token's audience. The Client must validate the audience according to the OpenID Connect rules before accepting the token. citeturn1search0

### `exp` — Expiration Time

`exp` identifies the time after which the ID Token must not be accepted for processing.

The Client must validate that the current time is before the expiration time, subject to the allowed clock-skew rules of the protocol. citeturn1search0

### `iat` — Issued At

`iat` identifies the time at which the ID Token was issued.

It provides temporal context for the token and is part of the ID Token validation rules. citeturn1search0

## 6. Authentication-Related Claims

OIDC also defines Claims that describe the authentication event.

### `nonce`

`nonce` binds an ID Token to a value that was sent in the Authentication Request.

When a `nonce` is present in the Authentication Request, the Client must verify that the corresponding value is present in the ID Token and matches the value associated with the authentication transaction. OIDC uses this mechanism to help associate the received ID Token with the request that initiated the authentication. citeturn1search0

Modern OAuth security guidance also treats the nonce as a transaction-specific value when it is used as a protection mechanism. citeturn0search0

### `auth_time`

`auth_time` records the time at which the End-User authentication occurred.

It becomes particularly important when the Client requests authentication that must satisfy a maximum authentication age. The details of `max_age` and authentication-time requirements belong to the Authentication Request and validation topics rather than this foundational ID Token lecture. citeturn1search0

### `acr`

`acr` can identify the Authentication Context Class associated with the authentication performed.

The value is deployment- and policy-dependent. OIDC does not require every deployment to use one universal authentication-context vocabulary. citeturn1search0

## 7. Identity Claims Are Not All Profile Claims

An ID Token can contain Claims about the End-User, but the ID Token should not be understood as a complete user profile.

OIDC separates authentication-related identity information from the broader set of user claims available through mechanisms such as the UserInfo Endpoint.

```text
ID Token
   │
   ├── authentication context
   ├── issuer
   ├── subject
   ├── audience
   └── timing / transaction information

UserInfo Endpoint
   │
   └── user claims requested by the Client
```

This distinction prevents a common conceptual error: an ID Token is primarily an authentication result, not a general-purpose API response containing every attribute about the user.

## 8. Why the Signature Matters

The Client must not accept an ID Token merely because it has the expected JSON fields.

The token is protected cryptographically so the Client can establish that the Claims came from the expected issuer and were not modified after issuance.

The conceptual verification process is:

```text
Received ID Token
       │
       ▼
Parse JWT structure
       │
       ▼
Determine acceptable algorithm / key
       │
       ▼
Verify cryptographic protection
       │
       ▼
Validate OIDC Claims
       │
       ▼
Trusted authentication result
```

RFC 8725 emphasizes that successful cryptographic verification alone is not sufficient: applications must also ensure that the algorithm is appropriate for the application context and that the issuer and subject semantics are correctly validated. citeturn0search3

## 9. ID Token Validation Is a Protocol Operation

ID Token validation is not equivalent to decoding a JWT.

For the Authorization Code Flow, OpenID Connect Core requires the Client to validate the ID Token after receiving the Token Response. The validation includes cryptographic verification and validation of the relevant Claims. citeturn1search0

At a conceptual level:

```text
                ID Token
                    │
        ┌───────────┴───────────┐
        │                       │
 Cryptographic              Protocol
   validation               validation
        │                       │
        ├── signature           ├── iss
        └── algorithm            ├── sub
                                ├── aud
                                ├── exp
                                ├── iat
                                └── nonce (when applicable)
```

The exact validation rules depend on the flow and context. They should therefore be implemented from the applicable OIDC validation section rather than reduced to a generic JWT-validation recipe. citeturn1search0

## 10. ID Token and Access Token Have Different Jobs

The distinction between the two tokens is fundamental.

```text
ID Token
   │
   └── tells the Client about the authentication / identity result

Access Token
   │
   └── authorizes access to a protected resource
```

The Client should not send an ID Token to a Resource Server as though it were an Access Token.

Likewise, an Access Token should not automatically be interpreted as proof of the identity of the End-User.

OIDC and OAuth can participate in the same transaction, but their tokens have different protocol purposes.

## 11. Authorization Code Flow: Where the ID Token Appears

In the Authorization Code Flow, the browser first receives an Authorization Code from the Authorization Endpoint.

The Client then sends the code to the Token Endpoint.

```text
End-User
   │
   ▼
OP Authorization Endpoint
   │
   │ Authorization Code
   ▼
Client
   │
   │ Token Request
   ▼
OP Token Endpoint
   │
   ├── Access Token
   ├── ID Token
   └── Refresh Token (when applicable)
        │
        ▼
Client
```

OIDC Core requires an `id_token` parameter in a successful Token Response for an OpenID Connect Authorization Code Flow transaction. citeturn1search0

The Client then validates the ID Token before using its identity information.

## 12. Current Security Context

The ID Token specification must be understood together with current OAuth security guidance.

RFC 9700, published in January 2025, is the current IETF Best Current Practice for OAuth 2.0 security. It updates the older OAuth threat model and security guidance and deprecates less-secure modes of operation. citeturn0search0

For authorization-code transactions, RFC 9700 requires public clients to use PKCE and recommends PKCE for confidential clients. It also describes transaction-specific OIDC `nonce` values as a protection mechanism for confidential OIDC clients under specified conditions. citeturn0search0

These mechanisms are important to the security of the complete authentication transaction, but they should not be confused with the definition of the ID Token itself.

## 13. The Mental Model

The complete model for this lecture is:

```text
                Authentication Request
                         │
                         ▼
                 OpenID Provider
                         │
                         │ authenticates End-User
                         ▼
                      ID Token
                         │
          ┌──────────────┴──────────────┐
          │                             │
    Cryptographic                  OIDC Claims
      protection                         │
          │                     ┌───────┼────────┐
          │                     │       │        │
          │                    iss     sub      aud
          │                     │       │        │
          │                    exp     iat    nonce
          │
          └───────────────► Relying Party
                                  │
                                  ▼
                         Trusted Auth Result
```

The key idea is:

```text
ID Token ≠ Access Token
ID Token = OIDC authentication / identity artifact
JWT       = representation format
Signature = cryptographic protection
Claims    = protocol information that must be validated
```

Understanding this model prepares the next stage of the learning path: implementing and testing ID Token validation without confusing JWT parsing with OIDC trust decisions.

## References

### Primary Standards and Specifications

1. OpenID Connect Core 1.0 incorporating errata set 2 — OpenID Foundation
   https://openid.net/specs/openid-connect-core-1_0.html citeturn1search0

2. OpenID Connect Working Group Specifications — OpenID Foundation
   https://openid.net/wg/connect/specifications/ citeturn0search6

3. JSON Web Token (JWT) — RFC 7519, IETF
   https://www.rfc-editor.org/rfc/rfc7519.html citeturn0search5

4. JSON Web Token Best Current Practices — RFC 8725, IETF
   https://www.rfc-editor.org/rfc/rfc8725.html citeturn0search3

5. Best Current Practice for OAuth 2.0 Security — RFC 9700, IETF, January 2025
   https://www.rfc-editor.org/rfc/rfc9700.html citeturn0search0

### Supporting JOSE Specifications

6. JSON Web Signature (JWS) — RFC 7515, IETF
   https://www.rfc-editor.org/rfc/rfc7515.html

7. JSON Web Encryption (JWE) — RFC 7516, IETF
   https://www.rfc-editor.org/rfc/rfc7516.html
