# OpenID Connect

OpenID Connect (OIDC) is an **identity layer built on top of OAuth 2.0**. It allows a Client to verify the identity of an End-User based on authentication performed by an OpenID Provider (OP), and to obtain Claims about that End-User.

The current OpenID Connect Core specification is **OpenID Connect Core 1.0 incorporating errata set 2**, published in December 2023. The OpenID Foundation's specifications page identifies this as the current errata version of the Core specification. The newer OpenID Connect specifications and profiles do not replace Core; they extend or profile the OIDC ecosystem for particular use cases.

## 1. OAuth 2.0 Gives Access; OIDC Adds Identity

OAuth 2.0 defines a framework for obtaining and using **Access Tokens** to access protected resources. OAuth itself does not define a standard way for a Client to determine the identity of the person who authenticated.

OIDC extends the OAuth authorization process to add authentication and identity information.

The key distinction is:

- **OAuth 2.0:** "Can this Client obtain permission to access this resource?"
- **OpenID Connect:** "Who authenticated, and what identity information can the Client rely on?"

OIDC therefore does not replace OAuth 2.0. It uses OAuth 2.0 as its protocol foundation and adds identity-specific behavior.

## 2. The Core Roles

OIDC uses OAuth terminology and adds terminology specific to identity.

### End-User

The human who authenticates.

### OpenID Provider (OP)

An OAuth 2.0 Authorization Server that can authenticate the End-User and provide Claims about the authentication event and the End-User to the Client.

### Relying Party (RP)

An OAuth 2.0 Client that uses OpenID Connect to request authentication and Claims from an OP.

In practice, the same application can therefore be described in two ways:

```text
OAuth 2.0 terminology       OIDC terminology
------------------------------------------------
Authorization Server   ->   OpenID Provider (OP)
Client                 ->   Relying Party (RP)
Resource Owner         ->   End-User
```

The terminology changes because the protocol is now concerned not only with authorization, but also with authentication and identity.

## 3. How OIDC Extends an OAuth Request

An OIDC Authentication Request is an OAuth 2.0 Authorization Request with OIDC-specific parameters and scopes.

The most important signal is the `openid` scope.

```text
scope=openid
```

A Client requesting the `openid` scope is requesting OpenID Connect authentication rather than using the authorization endpoint only as an OAuth authorization mechanism.

A simplified request can therefore look like:

```http
GET /authorize?
    response_type=code&
    client_id=example-client&
    redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
    scope=openid
```

The OAuth parameters such as `response_type`, `client_id`, and `redirect_uri` come from the OAuth authorization framework. The `openid` scope identifies the request as an OpenID Connect request.

Additional OIDC parameters will be introduced later when the protocol is studied in detail. They should not be treated as prerequisites for understanding this basic model.

## 4. The OIDC Authentication Model

At a high level, the protocol follows this sequence:

```text
End-User
   │
   │ uses
   ▼
Relying Party (RP)
   │
   │ Authentication Request
   ▼
OpenID Provider (OP)
   │
   ├── authenticates End-User
   │
   ├── obtains authorization/consent when required
   │
   ▼
Authentication Response
   │
   ▼
Relying Party (RP)
```

With the Authorization Code Flow, the authorization endpoint returns an Authorization Code and the Client subsequently uses the Token Endpoint. OIDC then provides an **ID Token** containing Claims about the authentication event.

The ID Token is the mechanism that lets the RP establish an identity-related result from the OIDC authentication process. Its structure and validation rules are covered separately in the next lecture.

## 5. OIDC Is More Than a Login Button

It is common to describe OIDC as simply "OAuth for login." That is useful as an initial intuition, but it is incomplete.

OIDC defines interoperable protocol behavior for authentication and identity Claims, including:

- how an RP requests authentication;
- how an OP communicates the authentication result;
- how identity information is represented as Claims;
- how the RP can obtain additional Claims through the UserInfo Endpoint; and
- how the parties establish and validate the identity-related result.

These mechanisms allow independently implemented RPs and OPs to communicate using the same protocol rules.

## 6. OIDC and the OAuth Authorization Server

An OP is not a completely different type of server from an OAuth Authorization Server.

The relationship is:

```text
OAuth Authorization Server
        │
        │ implements OIDC capabilities
        ▼
OpenID Provider (OP)
```

An Authorization Server becomes an OpenID Provider when it supports the OIDC functionality required to authenticate End-Users and provide the corresponding identity information to Relying Parties.

This distinction matters when reading specifications: OAuth defines the authorization framework, while OIDC defines the identity layer that builds on it.

## 7. What This Lecture Establishes

The essential model to carry into the following lectures is:

```text
OAuth 2.0
   │
   │ authorization foundation
   ▼
OpenID Connect
   │
   ├── Authentication
   ├── Identity Claims
   └── ID Token
```

And the central relationship is:

```text
RP (Client)
    │
    │ requests authentication
    ▼
OP (Authorization Server)
    │
    │ authenticates End-User
    │
    │ returns OIDC authentication result
    ▼
RP
```

The next lectures can now examine the individual pieces without mixing their responsibilities: authentication flow, ID Tokens, Claims/UserInfo, discovery, registration, logout, and security validation.

## References

### Primary Standards

1. OpenID Connect Core 1.0 incorporating errata set 2 — OpenID Foundation
   https://openid.net/specs/openid-connect-core-1_0.html

2. OpenID Connect specifications — OpenID Foundation, current specifications and errata status
   https://openid.net/wg/connect/specifications/

3. OAuth 2.0 Authorization Framework — RFC 6749, IETF
   https://www.rfc-editor.org/rfc/rfc6749.html

### Current Security Guidance

4. OAuth 2.0 Security Best Current Practice — RFC 9700, IETF, January 2025
   https://www.rfc-editor.org/rfc/rfc9700.html

RFC 9700 is used here as the current security context for OAuth-based deployments. Detailed security requirements and attack mitigations are intentionally reserved for the dedicated security and validation lecture.
