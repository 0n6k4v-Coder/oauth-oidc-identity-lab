# OpenID Connect Authentication

OpenID Connect (OIDC) adds an **authentication protocol** to OAuth 2.0. The purpose of this layer is not merely to obtain authorization to a resource, but to allow a Relying Party (RP) to establish that an End-User has been authenticated by an OpenID Provider (OP), and to receive information about that authentication.

The current OpenID Connect Core specification is **OpenID Connect Core 1.0 incorporating errata set 2**. It defines the authentication protocol, including Authentication Requests, Authentication Responses, ID Tokens, and the rules that connect an authentication request to the resulting identity information. citeturn1search4

## 1. What OIDC Authentication Adds to OAuth

OAuth 2.0 provides an authorization framework. Its authorization request can result in an authorization code or tokens, but OAuth itself does not define a standard identity assertion for the Client.

OIDC adds that missing identity layer.

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
```

An OpenID Provider is therefore an OAuth 2.0 Authorization Server that is capable of authenticating the End-User and providing the OIDC-defined identity information to the RP.

## 2. Authentication Is an Interaction With the OpenID Provider

The RP does not authenticate the End-User itself as part of the OIDC protocol. Instead, it sends the End-User to the OP's Authorization Endpoint.

At a high level:

```text
End-User
   │
   │ interacts with
   ▼
OpenID Provider
   │
   │ authenticates End-User
   │
   │ obtains authorization/consent as applicable
   ▼
Authentication Result
   │
   ▼
Relying Party
```

The exact authentication mechanism used by the OP is not fixed by OIDC Core. An OP may use its own authentication system or an upstream identity provider. What matters to the RP is the protocol result and the claims that the OP provides according to OIDC.

This separation is fundamental:

```text
How the user proves identity
            │
            │ implementation / OP responsibility
            ▼
      OpenID Provider
            │
            │ standardized OIDC result
            ▼
       Relying Party
```

## 3. The Authentication Request

An OIDC authentication transaction begins when the RP constructs an **Authentication Request** and sends the End-User to the OP's Authorization Endpoint.

The request uses OAuth 2.0 authorization request parameters and adds OIDC semantics.

The defining OIDC requirement is the `openid` scope.

A simplified Authorization Code request is:

```http
GET /authorize?
    response_type=code&
    client_id=example-client&
    redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
    scope=openid
```

For a real deployment, the request will normally contain additional security parameters. Those parameters are deliberately treated separately in later lectures rather than being mixed into this foundational model.

The important idea here is:

```text
OAuth authorization request
          +
OIDC authentication semantics
          │
          ▼
OIDC Authentication Request
```

## 4. What Happens at the OpenID Provider

After receiving the request, the OP processes the authentication transaction.

Conceptually, the OP must determine the End-User's authenticated identity before producing the OIDC authentication result.

```text
RP
 │
 │ Authentication Request
 ▼
OP Authorization Endpoint
 │
 ├── identify the Client
 ├── authenticate the End-User
 ├── determine the authorization/consent result
 └── create the protocol response
 │
 ▼
RP
```

The internal login mechanism is intentionally outside the core interoperability contract. OIDC standardizes the protocol between the RP and OP rather than requiring every OP to authenticate users using one particular credential system.

## 5. The Authentication Result

For the Authorization Code Flow, the browser-facing authorization response contains an **Authorization Code**. The RP then exchanges that code at the Token Endpoint.

The OIDC authentication result is represented by an **ID Token**, which is returned in the token response for the Authorization Code Flow.

```text
Authorization Endpoint
        │
        │ Authorization Code
        ▼
       RP
        │
        │ Token Request
        ▼
   Token Endpoint
        │
        │ ID Token + tokens as applicable
        ▼
       RP
```

The ID Token is therefore not simply another Access Token. It is an OIDC identity artifact containing Claims about the authentication event and the End-User.

The detailed structure and validation of the ID Token belong to the next lecture.

## 6. Authentication and Authorization Are Different Results

The two concepts must remain separate.

```text
Authentication
    │
    └── establishes an identity-related result

Authorization
    │
    └── determines what the Client is allowed to access
```

A successful OIDC authentication does not automatically mean that the RP has access to every protected resource owned by the End-User.

Likewise, obtaining an OAuth Access Token does not by itself establish the OIDC identity of the End-User.

OIDC combines these protocol layers in one standardized transaction while keeping their purposes distinct.

## 7. The ID Token Connects the Authentication Transaction to Identity

The ID Token contains Claims that allow the RP to process the authentication result.

Among its important Claims is `sub`, the locally unique and never reassigned identifier for the End-User at the Issuer for the Client.

OIDC also defines the `nonce` mechanism for binding an authentication request to an ID Token. When a nonce is sent in the Authentication Request, the corresponding ID Token must contain the same value and the Client must verify it. citeturn1search4

The conceptual relationship is:

```text
Authentication Request
        │
        │ nonce (when used)
        ▼
OpenID Provider
        │
        │ authentication
        ▼
      ID Token
        │
        │ nonce + identity Claims
        ▼
Relying Party
```

The exact validation rules for `iss`, `sub`, `aud`, `exp`, `iat`, `nonce`, and other Claims should be studied as part of ID Token validation rather than reproduced here.

## 8. Authorization Code Flow and Current Security Practice

OIDC Core defines several flows, but modern deployments should not treat all historical OAuth/OIDC flows as equally appropriate.

RFC 9700, **Best Current Practice for OAuth 2.0 Security**, published in January 2025, updates the OAuth security guidance and deprecates less-secure modes. It recommends the Authorization Code response type because it avoids exposing Access Tokens in authorization URLs. citeturn0search0

For authorization-code transactions:

- Public clients **MUST use PKCE** under RFC 9700.
- Confidential clients are **RECOMMENDED to use PKCE** as well.
- For confidential OIDC clients, RFC 9700 also describes `nonce` as an alternative countermeasure under specific additional precautions. citeturn0search0

PKCE binds the authorization request to the later token request using a transaction-specific `code_verifier` and derived `code_challenge`. RFC 7636 defines this mechanism, with `S256` required when the client is capable of using it. citeturn1search1

These security mechanisms are introduced here to establish the current protocol context. Their implementation and attack model belong to later authorization and security lectures.

## 9. Public and Confidential Clients in OIDC Authentication

Client type affects how the authentication transaction is secured, but it does not change the fundamental OIDC model.

```text
                 OIDC Authentication
                         │
             ┌───────────┴───────────┐
             │                       │
       Public Client          Confidential Client
             │                       │
       cannot keep a           can keep credentials
       client secret            confidential
             │                       │
             └────── both request authentication ──────┘
```

A browser-based application must be evaluated according to its actual architecture rather than simply according to the framework it uses. Current IETF browser-based application guidance is documented in **RFC 10017**, published in August 2026. citeturn0search4

The client classification and its security consequences will be explored through the experiments rather than assumed from a framework name.

## 10. Native Applications and Public Clients

For native applications, RFC 8252 establishes that public native clients should use the system browser/external user-agent for authorization and must use PKCE. citeturn1search0turn1search3

This illustrates an important principle: the security properties of an OAuth/OIDC client are determined by where credentials can be kept confidential and how the authorization transaction is performed, not merely by whether the application has a graphical interface.

## 11. Authentication Learning Model

The complete conceptual model for this lecture is:

```text
                 End-User
                    │
                    │ interacts with
                    ▼
             OpenID Provider
                    │
             authenticates user
                    │
                    ▼
            Authentication Result
                    │
                    ▼
              ID Token / Claims
                    │
                    ▼
             Relying Party (RP)
```

For the Authorization Code Flow:

```text
RP
 │
 │ Authentication Request
 ▼
OP Authorization Endpoint
 │
 │ authenticate End-User
 │
 │ Authorization Code
 ▼
RP
 │
 │ Token Request
 ▼
OP Token Endpoint
 │
 │ ID Token
 ▼
RP
```

The essential distinction is:

```text
OAuth 2.0 → authorization framework
OIDC      → authentication + identity layer
ID Token  → standardized authentication/identity result
```

## References

### Primary Standards

1. OpenID Connect Core 1.0 incorporating errata set 2 — OpenID Foundation
   https://openid.net/specs/openid-connect-core-1_0.html citeturn1search4

2. OpenID Connect Specifications — OpenID Foundation
   https://openid.net/wg/connect/specifications/ citeturn0search5

3. OAuth 2.0 Authorization Framework — RFC 6749, IETF
   https://www.rfc-editor.org/rfc/rfc6749.html citeturn0search2

### Current OAuth Security Guidance

4. Best Current Practice for OAuth 2.0 Security — RFC 9700, IETF, January 2025
   https://www.rfc-editor.org/rfc/rfc9700.html citeturn0search0

5. Proof Key for Code Exchange by OAuth Public Clients — RFC 7636, IETF
   https://www.rfc-editor.org/rfc/rfc7636.html citeturn1search1

6. OAuth 2.0 for Native Apps — RFC 8252, IETF
   https://www.rfc-editor.org/rfc/rfc8252.html citeturn1search3

7. OAuth 2.0 for Browser-Based Applications — RFC 10017, IETF, August 2026
   https://www.rfc-editor.org/rfc/rfc10017.html citeturn0search4
