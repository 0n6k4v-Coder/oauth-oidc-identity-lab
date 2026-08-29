# Lecture 04 — Complete OAuth 2.0 Authorization Code Flow

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation → Protocol Integration
> **Prerequisite:** Understanding of OAuth 2.0 roles, authorization requests, authorization codes, and token exchange

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Explain the complete OAuth 2.0 Authorization Code Flow from beginning to end.
* Identify what each participant does at every stage of the flow.
* Distinguish the browser/user-agent interactions from direct client-to-server interactions.
* Explain why an authorization code is exchanged for an access token.
* Explain how the authorization server and client bind the authorization transaction together.
* Understand where `client_id`, `redirect_uri`, `scope`, `state`, and PKCE fit into the complete flow.
* Understand how the resulting access token is used to access a protected resource.
* Identify the major security boundaries in the flow.
* Understand where OpenID Connect extends the OAuth flow for authentication.
* Connect the abstract protocol to the Microsoft Entra laboratory.

---

# 2. From Individual Steps to One Complete Flow

The previous lectures examined parts of the OAuth flow separately.

We can now combine them.

At the highest level:

```text
Resource Owner
      │
      │ Authorization
      ▼
Authorization Server
      │
      │ Authorization Code
      ▼
Client
      │
      │ Access Token
      ▼
Resource Server
      │
      │ Protected Resource
      ▼
Client
```

RFC 6749 describes this as an interaction among four OAuth roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

The complete flow is not one single HTTP request.

It is a sequence of interactions involving:

```text
User Agent
Authorization Endpoint
Client
Token Endpoint
Resource Server
```

RFC 6749's abstract protocol flow describes the client obtaining authorization, exchanging an authorization grant for an access token, and then presenting that access token to the resource server.

---

# 3. The Complete Mental Model

For the Authorization Code Flow, a useful high-level model is:

```text
                     USER AGENT
                    (Browser)
                         │
                         │
                         ▼
                 Authorization
                    Endpoint
                         │
                         │
                  User authenticates
                  and gives consent
                         │
                         ▼
                 Authorization Code
                         │
                         │ Redirect
                         ▼
                       Client
                         │
                         │ Token Request
                         ▼
                  Token Endpoint
                         │
                         │ Access Token
                         ▼
                       Client
                         │
                         │ Authorization:
                         │ Bearer <token>
                         ▼
                 Resource Server
                         │
                         │ Protected Resource
                         ▼
                       Client
```

The most important thing to understand is that the authorization code and the access token have different purposes.

```text
Authorization Code
        │
        │ Temporary credential
        │
        ▼
   Token Endpoint
        │
        ▼
   Access Token
        │
        │ Used to access
        ▼
 Resource Server
```

The client does **not** normally use the authorization code to call the resource server.

The authorization code is exchanged for an access token.

---

# 4. Participants

Before following the flow, establish the role of each participant.

## 4.1 Resource Owner

The resource owner is the entity capable of granting access to a protected resource.

In a user-delegated scenario, this is normally:

```text
Resource Owner
      =
     User
```

The user authorizes the client to obtain limited access to resources.

---

## 4.2 Client

The client is the application requesting access to a protected resource.

For example:

```text
Your Web Application
```

The client initiates the authorization process and later uses the resulting access token.

---

## 4.3 Authorization Server

The authorization server is responsible for issuing access tokens after successfully processing the applicable authorization grant.

Examples include:

```text
Microsoft Entra ID
```

The authorization server also provides the authorization endpoint and token endpoint.

---

## 4.4 Resource Server

The resource server hosts the protected resource.

For example:

```text
Protected API
```

The client presents an access token when requesting the protected resource.

The resource server decides whether the presented access token is acceptable for the requested resource according to the applicable authorization system.

---

## 4.5 User Agent

The user agent is typically the user's browser.

It is important because the browser participates in the authorization interaction.

The client does not normally collect the user's authorization-server credentials itself.

Instead:

```text
Client
  │
  │ Redirect
  ▼
Browser
  │
  │ Interacts with
  ▼
Authorization Server
```

This separation is an important security boundary.

---

# 5. Step 0 — Client Registration

Before the runtime flow begins, the client must be registered with the authorization server.

Conceptually:

```text
Client
  │
  │ Registration
  ▼
Authorization Server
```

The authorization server associates the client with information such as:

```text
client_id
redirect_uri
client type
allowed scopes
```

The exact registration process is deployment-specific.

For a web application, the authorization server may also issue credentials for authenticating the client at the token endpoint.

For public clients, a static client secret cannot be treated as a reliable secret because the client cannot keep it confidential.

This distinction becomes important when discussing PKCE and client authentication.

---

# 6. Step 1 — The Client Starts Authorization

The client begins the flow by directing the user's browser to the authorization endpoint.

Conceptually:

```text
Client
  │
  │ Authorization Request
  ▼
User Agent
  │
  │
  ▼
Authorization Server
```

A simplified authorization request may look like:

```text
GET /authorize?
    response_type=code&
    client_id=CLIENT_ID&
    redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
    scope=read&
    state=RANDOM_VALUE
```

The exact parameters depend on the protocol and deployment.

For the Authorization Code Flow, `response_type=code` indicates that the client is requesting an authorization code.

RFC 6749 defines the authorization request parameters for the Authorization Code Grant, including `response_type`, `client_id`, and `redirect_uri` where applicable.

---

# 7. Why Does the Browser Participate?

A common misconception is:

```text
Client
   │
   │ Login request
   ▼
Authorization Server
```

as if the client directly sends the user's credentials to the authorization server.

That is not the intended model.

Instead:

```text
Client
   │
   │ Authorization Request
   ▼
Browser
   │
   │ User interaction
   ▼
Authorization Server
```

The authorization server handles the user's authentication interaction.

This provides an important separation:

```text
Application
     │
     │ Requests authorization
     ▼
Authorization Server
     │
     │ Authenticates user
     ▼
User
```

The application does not need to handle the authorization server's user credentials.

---

# 8. Step 2 — Authorization Server Validates the Request

The authorization server receives the authorization request.

It must validate the request before proceeding.

Conceptually:

```text
Authorization Request
        │
        ▼
┌───────────────────────────┐
│ Authorization Server      │
│                           │
│ Validate request          │
│ Validate client           │
│ Validate redirect URI     │
│ Validate requested scope  │
│ Validate other parameters │
└─────────────┬─────────────┘
              │
              ▼
         Continue / Reject
```

The exact validation rules depend on the authorization server and protocol profile.

One particularly important security check is the redirect URI.

The authorization server must ensure that the redirect URI is appropriately registered and validated.

Current OAuth Security BCP requires exact redirect URI matching, with the specific localhost exception for native apps described by RFC 8252.

---

# 9. Step 3 — User Authentication

Once the request is accepted, the authorization server authenticates the resource owner.

Conceptually:

```text
Browser
   │
   │
   ▼
Authorization Server
   │
   │ "Who are you?"
   ▼
User Authentication
```

The exact authentication mechanism is outside the core OAuth protocol.

For example, an authorization server might use:

```text
Password
MFA
Passkey
Enterprise SSO
Biometric authentication
```

OAuth itself is primarily concerned with authorization.

When OpenID Connect is used, authentication and identity information are added as an identity layer on top of OAuth 2.0.

OpenID Connect Core defines authentication using the Authorization Code Flow and the resulting ID Token processing.

---

# 10. Step 4 — Authorization / Consent

After authentication, the authorization server determines whether the resource owner grants the requested access.

Conceptually:

```text
User
 │
 │
 ▼
Authorization Server
 │
 │
 │ "Do you allow this client
 │  to request these permissions?"
 │
 ▼
Consent / Authorization Decision
```

The requested permissions may be represented using OAuth scopes.

For example:

```text
scope=profile.read messages.read
```

The important point is:

```text
Requested Scope
      ≠
Automatically Granted Scope
```

The authorization server determines what authorization is actually granted.

The resulting authorization code represents the authorization grant that the client can use to request an access token.

---

# 11. Step 5 — The Authorization Server Issues the Code

If authorization succeeds:

```text
Authorization Server
        │
        │ Authorization Code
        ▼
      Browser
        │
        │ Redirect
        ▼
      Client
```

The browser is redirected to the client's registered redirect URI.

Conceptually:

```text
HTTP 302
Location:
https://client.example/callback?
    code=AUTHORIZATION_CODE&
    state=RANDOM_VALUE
```

The code is delivered to the client through the user agent.

The authorization code is not the access token.

It is a temporary credential used in the next step.

RFC 6749 specifies that the authorization server returns the authorization code through the client's redirection URI after a successful authorization decision.

---

# 12. Why Use an Authorization Code?

This is one of the central ideas of the flow.

Instead of:

```text
Authorization Server
        │
        │ Access Token
        ▼
      Browser
        │
        ▼
      Client
```

the Authorization Code Flow uses:

```text
Authorization Server
        │
        │ Authorization Code
        ▼
      Browser
        │
        ▼
      Client
        │
        │ Token Exchange
        ▼
Authorization Server
        │
        │ Access Token
        ▼
      Client
```

This creates a separation between:

```text
Front-Channel
```

and:

```text
Back-Channel
```

The authorization response travels through the user's browser.

The token exchange occurs directly between the client and the authorization server.

That separation is an important security property of the Authorization Code Flow.

Current OAuth Security BCP recommends authorization-code-based responses rather than response types that directly issue access tokens at the authorization endpoint.

---

# 13. Step 6 — Client Receives the Authorization Code

The client receives something conceptually like:

```text
/callback?
    code=AUTHORIZATION_CODE&
    state=RANDOM_VALUE
```

At this point:

```text
Client has:
    Authorization Code

Client does NOT yet have:
    Access Token
```

The client should also validate the transaction state according to the security mechanisms being used.

For OAuth clients, `state` can provide CSRF protection when PKCE or another appropriate mechanism is not being relied upon.

Current OAuth Security BCP requires clients to prevent CSRF and discusses PKCE, OIDC `nonce`, and `state` as relevant protections.

---

# 14. Step 7 — Client Exchanges the Code

The client now sends a request to the token endpoint.

Conceptually:

```text
Client
  │
  │ Authorization Code
  │
  │ + Client Authentication
  │ + PKCE code_verifier
  │
  ▼
Token Endpoint
```

A simplified request:

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https%3A%2F%2Fclient.example%2Fcallback&
client_id=CLIENT_ID&
code_verifier=CODE_VERIFIER
```

Not every parameter is required in every deployment.

For example, the exact client authentication method depends on the client type and authorization-server configuration.

---

# 15. PKCE in the Complete Flow

PKCE adds an additional binding between the authorization request and the later token request.

The client first creates:

```text
code_verifier
```

Then derives:

```text
code_challenge
```

For the recommended S256 method:

```text
code_challenge =
    BASE64URL(
        SHA256(
            ASCII(code_verifier)
        )
    )
```

The client sends the challenge during the authorization request:

```text
Authorization Request
        │
        └── code_challenge
```

Later, it sends the original verifier:

```text
Token Request
        │
        └── code_verifier
```

The authorization server checks that they correspond.

Conceptually:

```text
Authorization Request
        │
        │ code_challenge
        ▼
Authorization Server
        │
        │ remembers binding
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
        │ Verify
        ▼
Token Issuance
```

RFC 7636 defines PKCE to mitigate authorization-code interception attacks. Current OAuth Security BCP goes further: authorization servers must support PKCE, public clients must use it, and the `S256` method is the currently recommended method because it does not expose the verifier in the authorization request.

---

# 16. Step 8 — Authorization Server Validates the Token Request

The authorization server does not simply exchange any code for a token.

It validates the token request.

Conceptually:

```text
Token Request
      │
      ▼
┌────────────────────────────┐
│ Authorization Server       │
│                            │
│ Validate client            │
│ Validate authorization code│
│ Validate redirect URI      │
│ Validate PKCE              │
│ Validate other conditions  │
└─────────────┬──────────────┘
              │
              ▼
        Token Issuance
```

The authorization server may reject the request if:

```text
Authorization Code is invalid
Authorization Code is expired
Authorization Code was already used
Client does not match
Redirect URI does not match
PKCE verification fails
Client authentication fails
```

RFC 6749 specifies validation of the authorization code, client, and redirect URI at the token endpoint.

Current OAuth Security BCP additionally requires protections against authorization-code injection and misuse.

---

# 17. Step 9 — Authorization Server Issues the Access Token

If validation succeeds:

```text
Authorization Server
        │
        │ Token Response
        ▼
      Client
```

A conceptual response may contain:

```json
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "profile.read"
}
```

Depending on the flow and authorization-server behavior, the response may also contain:

```text
refresh_token
```

or, in an OpenID Connect flow:

```text
id_token
```

The important distinction is:

```text
Access Token
    ↓
Used to access protected resources

ID Token
    ↓
Used by OpenID Connect to communicate authentication information
```

Do not treat the two tokens as interchangeable.

OpenID Connect Core explicitly defines the ID Token as part of its authentication layer and separately discusses access-token validation.

---

# 18. Step 10 — Client Calls the Resource Server

The client now has the credential it needs to request the protected resource.

Conceptually:

```text
Client
  │
  │ GET /api/profile
  │ Authorization: Bearer ACCESS_TOKEN
  ▼
Resource Server
```

A simplified request:

```http
GET /api/profile HTTP/1.1
Host: api.example.com
Authorization: Bearer ACCESS_TOKEN
```

OAuth bearer-token usage defines the use of the `Authorization` HTTP header for presenting a bearer access token.

The important concept is:

```text
Authorization Server
        │
        │ Issues token
        ▼
      Client
        │
        │ Presents token
        ▼
 Resource Server
```

The client does not normally send the authorization code to the resource server.

---

# 19. Step 11 — Resource Server Validates the Access Token

The resource server receives the request.

It must determine whether the access token is acceptable for the requested resource.

Conceptually:

```text
Access Token
     │
     ▼
Resource Server
     │
     ├── Valid?
     ├── Not expired?
     ├── Correct audience/resource?
     ├── Appropriate scope?
     └── Other applicable checks
     │
     ▼
Allow / Deny
```

The exact validation mechanism depends on the token format and authorization-server/resource-server architecture.

An access token is an authorization credential.

It should not automatically be interpreted as an identity assertion.

This distinction is particularly important when the access token is a JWT.

```text
JWT
 │
 └── A token representation format

Access Token
 │
 └── An OAuth authorization credential
```

Therefore:

```text
Access Token ≠ JWT
```

A provider may issue a JWT access token, but OAuth does not require all access tokens to be JWTs.

---

# 20. Step 12 — Protected Resource Is Returned

If the access token is accepted:

```text
Resource Server
        │
        │ Protected Resource
        ▼
      Client
```

For example:

```json
{
  "id": "12345",
  "name": "Example User",
  "department": "Engineering"
}
```

The client can then present the resulting data to the user.

The complete authorization process has now reached the protected resource.

---

# 21. The Complete Flow in One Diagram

Putting everything together:

```text
┌──────────────────┐
│      User        │
│ Resource Owner   │
└────────┬─────────┘
         │
         │ Uses
         ▼
┌──────────────────┐
│   User Agent     │
│     Browser      │
└────────┬─────────┘
         │
         │ Authorization Request
         │ response_type=code
         │ client_id
         │ redirect_uri
         │ scope
         │ state
         │ code_challenge
         ▼
┌──────────────────────────┐
│   Authorization Server   │
│                          │
│ Authenticate User        │
│ Obtain Authorization     │
│ Issue Authorization Code │
└────────────┬─────────────┘
             │
             │ Redirect
             │ code
             │ state
             ▼
       ┌──────────────┐
       │    Client    │
       │              │
       │ Verify       │
       │ transaction  │
       └──────┬───────┘
              │
              │ Token Request
              │ code
              │ redirect_uri
              │ code_verifier
              │ client authentication
              ▼
┌──────────────────────────┐
│   Token Endpoint         │
│                          │
│ Validate Code            │
│ Validate Client          │
│ Validate Redirect URI    │
│ Validate PKCE            │
└────────────┬─────────────┘
             │
             │ Access Token
             ▼
       ┌──────────────┐
       │    Client    │
       └──────┬───────┘
              │
              │ Authorization:
              │ Bearer <access-token>
              ▼
┌──────────────────────────┐
│    Resource Server       │
│                          │
│ Validate Access Token    │
│ Check Authorization      │
└────────────┬─────────────┘
             │
             │ Protected Resource
             ▼
       ┌──────────────┐
       │    Client    │
       └──────────────┘
```

---

# 22. Front Channel vs Back Channel

One of the most useful ways to understand the architecture is to separate the communication paths.

## Front Channel

The front channel generally involves the user's browser.

```text
Client
  │
  │ Authorization Request
  ▼
Browser
  │
  ▼
Authorization Server
  │
  │ Authorization Response
  ▼
Browser
  │
  ▼
Client
```

The authorization code travels through this browser-mediated interaction.

---

## Back Channel

The token exchange is a direct interaction between the client and the authorization server.

```text
Client
  │
  │ Token Request
  ▼
Authorization Server
  │
  │ Token Response
  ▼
Client
```

The access token can then be sent directly from the client to the resource server.

```text
Client
  │
  │ Access Token
  ▼
Resource Server
```

This distinction is important because different credentials have different exposure characteristics.

---

# 23. Why the Authorization Code Is Short-Lived

The authorization code travels through a browser redirect.

That makes it a credential that requires protection.

Conceptually:

```text
Authorization Code
        │
        ├── Short-lived
        ├── Bound to transaction
        ├── Bound to client
        └── Exchanged for token
```

If an attacker obtains a code, the attacker should not automatically be able to exchange it successfully.

The authorization server can enforce bindings such as:

```text
Client
+
Redirect URI
+
PKCE
+
Code validity
+
One-time use
```

Current OAuth Security BCP specifically addresses authorization-code injection, interception, and misuse.

---

# 24. The Security Boundaries of the Flow

A useful way to analyze the complete flow is to identify where trust changes.

```text
                 TRUST BOUNDARIES

User
 │
 ▼
Browser
 │
 ├─────────────── Front Channel ───────────────┐
 │                                             │
 ▼                                             ▼
Authorization Server                    Client
 │                                             │
 │                                             │
 └──────────── Back Channel ───────────────────┘
                                               │
                                               │ Access Token
                                               ▼
                                        Resource Server
```

Each boundary requires appropriate validation.

For example:

```text
Authorization Request
        ↓
Validate client / redirect URI / parameters

Authorization Response
        ↓
Validate transaction / state / PKCE context

Token Request
        ↓
Validate code / client / redirect URI / PKCE

Resource Request
        ↓
Validate access token / authorization
```

OAuth security is therefore not one single validation step.

It is a sequence of security decisions.

---

# 25. Where PKCE Protects the Flow

PKCE primarily protects the connection between:

```text
Authorization Request
```

and:

```text
Token Request
```

Conceptually:

```text
          Authorization Request
                  │
                  │ code_challenge
                  ▼
             Authorization
                Server
                  │
                  │ Authorization Code
                  ▼
                Client
                  │
                  │ code_verifier
                  ▼
             Token Endpoint
                  │
                  │ Verify relationship
                  ▼
             Access Token
```

An attacker who obtains the authorization code but does not possess the corresponding `code_verifier` should not be able to successfully redeem the code.

RFC 7636 defines this mechanism specifically to mitigate authorization-code interception. RFC 9700 now requires authorization servers to support PKCE and requires public clients to use it.

---

# 26. What Happens If Something Goes Wrong?

The flow is not always successful.

For example:

```text
User denies authorization
```

or:

```text
Invalid client
```

or:

```text
Invalid redirect URI
```

or:

```text
Invalid authorization code
```

or:

```text
PKCE verification failure
```

or:

```text
Invalid scope
```

The authorization server or token endpoint can return an OAuth error response appropriate to the failed operation.

Therefore the real flow is:

```text
Request
  │
  ▼
Validation
  │
  ├───────────────┐
  │               │
Success          Failure
  │               │
  ▼               ▼
Continue        Error
```

A production implementation must handle both branches.

---

# 27. OAuth 2.0 Does Not Equal Login

At this point, an important distinction must be preserved.

OAuth 2.0 gives us:

```text
Authorization
```

The flow allows a client to obtain an access token representing authorization to access protected resources.

It does not, by itself, standardize how a client learns the identity of the user.

For authentication and standardized identity information, OpenID Connect adds an identity layer on top of OAuth 2.0. OpenID Connect Core defines the Authorization Code Flow, ID Token, authentication response validation, and ID Token validation.

---

# 28. OAuth 2.0 and OpenID Connect Together

In an OpenID Connect Authorization Code Flow, the conceptual architecture becomes:

```text
User
 │
 ▼
Browser
 │
 │ OIDC Authentication Request
 ▼
OpenID Provider
 │
 │ Authorization Code
 ▼
Client / Relying Party
 │
 │ Token Request
 ▼
OpenID Provider
 │
 │ ID Token
 │ Access Token
 ▼
Client
 │
 ├── ID Token
 │      │
 │      └── Authentication / Identity
 │
 └── Access Token
        │
        └── Protected Resource Access
```

This is why the two tokens must not be confused.

```text
ID Token
    ↓
"Information about the authentication
 of the End-User"

Access Token
    ↓
"Credential used to access
 a protected resource"
```

OpenID Connect Core defines the ID Token as a JWT containing claims about the authentication and subject, while the access token is used to access protected resources.

---

# 29. Microsoft Entra Mental Model

For the laboratory, Microsoft Entra ID can be viewed conceptually as the authorization server / OpenID Provider participating in the flow.

A simplified model:

```text
                 Microsoft Entra ID
              ┌─────────────────────┐
              │                     │
User ────────►│ Authorization       │
              │ Endpoint            │
              │                     │
              │ Token Endpoint      │
              └──────────┬──────────┘
                         │
                         │ Tokens
                         ▼
                    Your Client
                         │
                         │ Access Token
                         ▼
                    Protected API
```

When OpenID Connect is involved:

```text
Microsoft Entra ID
        │
        ├── ID Token
        │      ↓
        │   Identity
        │
        └── Access Token
               ↓
          API Authorization
```

The exact Microsoft Entra endpoints, token contents, audiences, scopes, and application-registration settings will be investigated in later laboratory exercises.

---

# 30. One Complete Transaction

It is useful to compress the entire lecture into one transaction.

```text
1. User wants to use the application.

2. Client creates an authorization request.

3. Client redirects the browser to the authorization endpoint.

4. Authorization server validates the request.

5. Authorization server authenticates the user.

6. Authorization server obtains the authorization decision.

7. Authorization server redirects the browser back to the client.

8. Authorization code is delivered to the client.

9. Client validates the transaction context.

10. Client sends the authorization code to the token endpoint.

11. Client proves the appropriate binding,
    such as PKCE and/or client authentication.

12. Authorization server validates the request.

13. Authorization server issues an access token.

14. Client sends the access token to the resource server.

15. Resource server validates the access token.

16. Resource server evaluates the request.

17. Resource server returns the protected resource.
```

The important sequence is:

```text
Authorization
      ↓
Authorization Code
      ↓
Token Exchange
      ↓
Access Token
      ↓
Protected Resource
```

---

# 31. What Each Credential Is For

The complete flow becomes easier to understand when the credentials are separated.

| Credential                              | Purpose                                                        | Main Destination       |
| --------------------------------------- | -------------------------------------------------------------- | ---------------------- |
| `client_id`                             | Identifies the OAuth client                                    | Authorization Server   |
| `client_secret` / client authentication | Authenticates a confidential client when applicable            | Token Endpoint          |
| `authorization code`                    | Represents the authorization grant and is exchanged for tokens | Token Endpoint          |
| `code_verifier`                         | Proves possession of the PKCE secret                           | Token Endpoint          |
| `access token`                          | Authorizes access to a protected resource                      | Resource Server        |
| `ID Token`                              | Communicates authentication/identity information in OIDC       | Client / Relying Party |

The exact credential set depends on the client type and protocol profile.

---

# 32. The Most Important Mental Model

Do not memorize the flow merely as a list of URLs.

Understand the purpose of each transition:

```text
                 WHY?

Client
  │
  │ "I need authorization."
  ▼
Authorization Endpoint
  │
  │ "The user decides."
  ▼
Authorization Code
  │
  │ "This is a temporary authorization grant."
  ▼
Token Endpoint
  │
  │ "Prove the transaction and exchange the grant."
  ▼
Access Token
  │
  │ "Use this authorization credential."
  ▼
Resource Server
  │
  │ "Does this token authorize this request?"
  ▼
Protected Resource
```

That is the conceptual heart of the Authorization Code Flow.

---

# 33. Security Checklist

When reviewing an Authorization Code implementation, ask:

```text
[ ] Is HTTPS used?

[ ] Is the redirect URI securely registered?

[ ] Is exact redirect URI matching enforced?

[ ] Is authorization code replay prevented?

[ ] Is PKCE used?

[ ] Is S256 used for PKCE?

[ ] Is the PKCE verifier kept secret from the authorization request?

[ ] Is the authorization transaction protected against CSRF?

[ ] Is state handled correctly where applicable?

[ ] Is the authorization code exchanged at the token endpoint?

[ ] Are client authentication requirements correctly applied?

[ ] Are access tokens sent securely to the resource server?

[ ] Does the resource server validate the access token?

[ ] Are scopes / permissions checked?

[ ] Is an ID Token incorrectly being used as an API access token?
```

Current OAuth Security BCP specifically recommends exact redirect URI matching, PKCE, protection against CSRF and authorization-code injection, and secure handling of redirect-based authorization responses.

---

# 34. Native Applications

The same conceptual Authorization Code Flow can also be used by native applications, but the security architecture differs from a confidential web server.

For native applications:

```text
Native App
    │
    │ Authorization Request
    ▼
External User Agent
    │
    ▼
Authorization Server
```

RFC 8252 specifies that native applications should use an external user-agent, primarily the user's browser, rather than embedding the authorization interaction inside the application. Public native clients must implement PKCE.

This is an example of why:

```text
OAuth Flow
    ≠
One identical implementation everywhere
```

The protocol concepts remain, but client type and deployment architecture affect the security requirements.

---

# 35. Current OAuth Security Guidance

RFC 6749 remains the foundational OAuth 2.0 specification, but it should not be studied in isolation.

The RFC Editor explicitly notes that RFC 6749 has been updated by:

```text
RFC 8252
OAuth 2.0 for Native Apps

RFC 8996
Deprecating TLS 1.0 and TLS 1.1

RFC 9700
Best Current Practice for OAuth 2.0 Security
```

For this lecture, RFC 9700 is particularly important because it describes current security practices for OAuth deployments, including:

```text
PKCE
Redirect URI validation
CSRF protection
Authorization code injection protection
Open redirector protection
Secure authorization responses
```

Therefore, the correct way to understand the flow is:

```text
RFC 6749
    ↓
Core OAuth 2.0 Flow

        +

RFC 7636
    ↓
PKCE

        +

RFC 9700
    ↓
Current OAuth Security Best Practice

        +

RFC 8252
    ↓
Native Application Considerations
```

---

# 36. Lecture Summary

The complete Authorization Code Flow can be reduced to:

```text
1. Client creates authorization request.

2. Browser is redirected to authorization server.

3. Authorization server authenticates the user.

4. User authorizes the requested access.

5. Authorization server returns an authorization code.

6. Client receives the authorization code.

7. Client exchanges the code at the token endpoint.

8. Authorization server validates the request.

9. Authorization server issues an access token.

10. Client presents the access token to the resource server.

11. Resource server validates authorization.

12. Protected resource is returned.
```

The fundamental separation is:

```text
Browser / Front Channel
        │
        │ Authorization Code
        ▼
      Client
        │
        │ Back-Channel Token Exchange
        ▼
Authorization Server
        │
        │ Access Token
        ▼
      Client
        │
        │ Resource Request
        ▼
Resource Server
```

And the most important conceptual distinction is:

```text
Authorization Code
        ≠
Access Token
        ≠
ID Token
```

Each exists for a different purpose.

---

# 37. Knowledge Check

Before moving forward, you should be able to answer these without looking at the lecture.

### Question 1

Why does the Authorization Code Flow use an authorization code instead of immediately returning an access token through the browser?

---

### Question 2

Which component normally handles the user's authentication?

```text
A. Client
B. Resource Server
C. Authorization Server
D. Database
```

---

### Question 3

Where is the authorization code exchanged for an access token?

```text
A. Resource Server
B. Authorization Endpoint
C. Token Endpoint
D. Browser
```

---

### Question 4

What does PKCE bind together?

Explain the relationship between:

```text
code_challenge
```

and:

```text
code_verifier
```

---

### Question 5

Should a client send the authorization code to the Resource Server?

Why?

---

### Question 6

What is the primary purpose of an access token?

---

### Question 7

Is an access token necessarily a JWT?

Explain why or why not.

---

### Question 8

In OpenID Connect, what is the purpose of the ID Token?

---

### Question 9

Why is redirect URI validation a security-critical part of the flow?

---

### Question 10

Describe the complete flow in one sentence.

A good answer should be able to express something similar to:

```text
The client obtains user authorization through the authorization
server, receives an authorization code, exchanges it for an
access token, and uses that access token to access a protected
resource.
```

---

# 38. What Comes Next?

The OAuth flow is now complete at the protocol level.

The next stage of the laboratory can move from:

```text
"I understand the flow."
```

to:

```text
"I can observe and verify the flow."
```

The next topics can therefore investigate the concrete artifacts produced by the flow:

```text
Authorization Request
        ↓
Authorization Code
        ↓
Token Request
        ↓
Token Response
        ↓
Access Token
        ↓
Protected Resource
```

From there, the laboratory can examine how these concepts become concrete in Microsoft Entra ID.

---

# 39. References

## 39.1 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

**Authority:** Internet Engineering Task Force (IETF)

RFC 6749 defines the foundational OAuth 2.0 framework, including:

* OAuth roles
* Authorization grants
* Authorization Code Grant
* Authorization endpoint
* Token endpoint
* Access tokens
* Scope
* Authorization Code Flow

Official source:

https://www.rfc-editor.org/rfc/rfc6749.html

The RFC Editor notes that RFC 6749 has been updated by RFC 8252, RFC 8996, and RFC 9700.

Relevant sections:

```text
Section 1.1 — Roles
Section 1.2 — Protocol Flow
Section 1.3.1 — Authorization Code
Section 2 — Client Registration
Section 3.1 — Authorization Endpoint
Section 3.2 — Token Endpoint
Section 3.3 — Access Token Scope
Section 4.1 — Authorization Code Grant
Section 4.1.1 — Authorization Request
Section 4.1.2 — Authorization Response
Section 4.1.3 — Access Token Request
Section 4.1.4 — Access Token Response
```

---

## 39.2 IETF RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

**Authority:** Internet Engineering Task Force (IETF)

RFC 7636 defines PKCE and addresses authorization-code interception attacks against OAuth public clients.

Official source:

https://www.rfc-editor.org/rfc/rfc7636.html

Relevant sections:

```text
Section 1 — Introduction
Section 1.1 — Protocol Flow
Section 4 — Protocol
Section 4.1 — Client Creates a Code Verifier
Section 4.2 — Client Creates the Code Challenge
Section 4.5 — Client Sends the Authorization Request
Section 4.6 — Client Sends the Authorization Code Request
```

---

## 39.3 IETF RFC 9700 — Best Current Practice for OAuth 2.0 Security

**Authority:** Internet Engineering Task Force (IETF)

RFC 9700 provides current security guidance for OAuth 2.0 deployments.

It is particularly relevant to this lecture because it updates the security interpretation of the Authorization Code Flow.

Official source:

https://www.rfc-editor.org/rfc/rfc9700.html

Relevant topics:

```text
Section 2.1 — Protecting Redirect-Based Flows
Section 2.1.1 — Authorization Code Grant
Section 4.1 — Redirect URI Validation Attacks
Section 4.5 — Authorization Code Injection
Section 4.7 — Cross-Site Request Forgery
Section 4.11 — Open Redirection
```

Important current guidance includes:

```text
Exact redirect URI matching
PKCE support
PKCE for public clients
Protection against authorization-code injection
CSRF protection
Secure redirect handling
```

---

## 39.4 IETF RFC 8252 — OAuth 2.0 for Native Apps

**Authority:** Internet Engineering Task Force (IETF)

RFC 8252 defines Best Current Practice for OAuth authorization requests from native applications.

Official source:

https://www.rfc-editor.org/rfc/rfc8252.html

Relevant topics:

```text
External User-Agent
Authorization Code Flow for Native Apps
PKCE
Redirect URI handling
Public native clients
```

---

## 39.5 OpenID Connect Core 1.0 — Incorporating Errata Set 2

**Authority:** OpenID Foundation

OpenID Connect Core defines an identity layer on top of OAuth 2.0.

Official source:

https://openid.net/specs/openid-connect-core-1_0.html

Relevant sections:

```text
Section 2 — ID Token
Section 3.1 — Authentication using the Authorization Code Flow
Section 3.1.1 — Authorization Code Flow Steps
Section 3.1.2 — Authorization Endpoint
Section 3.1.3 — Token Endpoint
Section 3.1.3.6 — ID Token
Section 3.1.3.7 — ID Token Validation
Section 3.1.3.8 — Access Token Validation
Section 16 — Security Considerations
```

The current published Core specification incorporates errata set 2 and explicitly defines authentication on top of OAuth 2.0, ID Tokens, authentication responses, and token validation.

---

## 39.6 Source Selection Note

This lecture uses the standards according to their roles:

```text
RFC 6749
    │
    └── OAuth 2.0 Core Flow

RFC 7636
    │
    └── PKCE

RFC 9700
    │
    └── Current OAuth Security Best Practice

RFC 8252
    │
    └── Native Application Security

OpenID Connect Core
    │
    └── Authentication / ID Token Layer
```

The lecture does not treat RFC 6749 as the complete modern security specification.

Instead:

```text
Protocol Foundation
        +
Current Security Guidance
        +
OIDC Identity Layer
        ↓
Modern Understanding of the Flow
```
