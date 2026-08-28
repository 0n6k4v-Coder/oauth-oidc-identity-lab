# Lecture 01 — The Authorization Request

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Module:** OAuth / OIDC Flow  
> **Level:** Intermediate Foundation  
> **Prerequisite:** Authentication vs Authorization, OAuth 2.0 Overview, OpenID Connect Overview, and Identity Providers

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain the purpose of an authorization request.
- Identify the endpoint to which the request is sent.
- Explain the roles of `client_id`, `redirect_uri`, `response_type`, `scope`, and `state`.
- Understand how an OAuth 2.0 authorization request differs when OpenID Connect is added.
- Explain why a server must validate the authorization request instead of blindly trusting its parameters.
- Recognize the security purpose of `state`, `nonce`, PKCE, and exact redirect URI matching.
- Connect the protocol-level request to the Microsoft Entra ID login flow used later in this lab.

---

# 2. Where We Are in the Flow

In the Authorization Code flow, the authorization request is the point where the Client sends the user's browser to the Authorization Server.

Conceptually:

```text
User
 │
 │  Opens application
 ▼
Client / Your Application
 │
 │  1. Build authorization request
 │
 │  2. Redirect browser
 ▼
Authorization Server / Identity Provider
 │
 │  Authenticate user
 │  Obtain / evaluate authorization
 │
 ▼
Redirect back to Client
```

The important point is:

> The Client does not normally ask the user to send their password to the Client for this flow. Instead, the Client redirects the User Agent to the Authorization Server.

RFC 6749 defines this request as part of the authorization endpoint interaction.

---

# 3. What Is an Authorization Request?

An authorization request is a request sent by the Client, through the User Agent, to the Authorization Server's authorization endpoint.

A simplified example looks like this:

```text
GET /authorize?
    response_type=code
    &client_id=CLIENT_ID
    &redirect_uri=https://app.example.com/callback
    &scope=openid profile email
    &state=RANDOM_VALUE
```

The actual request URL may be much longer because the parameters are URL encoded.

Conceptually:

```text
Client
  │
  │ "Please begin authorization for this client,
  │  for these requested scopes, and return the result here."
  ▼
Authorization Server
```

The request does **not** itself prove that the user has authenticated. Authentication occurs at the Authorization Server as part of the overall flow.

---

# 4. The Authorization Endpoint

OAuth 2.0 defines an authorization endpoint as the endpoint used by the Client to obtain authorization from the Resource Owner through User-Agent redirection.

A typical structure is:

```text
https://authorization-server.example/authorize
```

For a real provider, the Client should use the provider's documented endpoints or, when using OpenID Connect discovery, obtain the authorization endpoint from the provider's discovery metadata.

Conceptually:

```text
Client
 │
 │ Redirect User Agent
 ▼
┌───────────────────────────┐
│ Authorization Endpoint    │
│                           │
│ /authorize                │
└─────────────┬─────────────┘
              │
              ▼
      Authorization Server
```

The exact endpoint is provider-specific. The protocol defines the role and required behavior; the provider publishes the actual endpoint URL.

---

# 5. Core OAuth 2.0 Parameters

## 5.1 `response_type`

`response_type` tells the Authorization Server which type of response the Client expects from the authorization endpoint.

For the Authorization Code flow:

```text
response_type=code
```

Conceptually:

```text
Client requests:

response_type=code

        ↓

Authorization Server returns:

Authorization Code
```

The authorization code is not the same thing as an access token.

It is a temporary credential that the Client later exchanges at the token endpoint.

---

## 5.2 `client_id`

`client_id` identifies the Client to the Authorization Server.

Example:

```text
client_id=abc123...
```

Important:

> `client_id` is an identifier, not a secret.

A browser can see it because it is included in the authorization request.

The Authorization Server uses it to identify which registered application is making the request and to apply the configuration associated with that Client.

For example:

```text
client_id
    │
    ▼
Registered Client
    │
    ├── Allowed redirect URIs
    ├── Allowed grant types
    ├── Allowed scopes / permissions
    └── Other provider-specific configuration
```

---

## 5.3 `redirect_uri`

`redirect_uri` tells the Authorization Server where the User Agent should be redirected after the authorization response.

Example:

```text
redirect_uri=https://app.example.com/oauth/callback
```

Later, a successful authorization response may conceptually become:

```text
https://app.example.com/oauth/callback
    ?code=AUTHORIZATION_CODE
    &state=RANDOM_VALUE
```

The redirect URI is security-sensitive.

If an attacker could freely choose it, an authorization response might be sent to an attacker-controlled location.

Therefore, Authorization Servers commonly require redirect URIs to match registered Client configuration according to the applicable protocol and provider rules.

---

## 5.4 `scope`

`scope` expresses the access requested by the Client.

Example:

```text
scope=read write
```

For OpenID Connect:

```text
scope=openid profile email
```

Conceptually:

```text
Client requests:

read profile

        │
        ▼
Authorization Server evaluates request
        │
        ├── Allowed → grant appropriate authorization
        │
        └── Not allowed → reject or reduce authorization,
                       depending on protocol/provider behavior
```

A Client cannot securely give itself more permissions simply by changing the URL parameter.

The Authorization Server is responsible for issuing the resulting authorization according to its policies and registered Client configuration.

---

## 5.5 `state`

OAuth 2.0 allows the Client to include a `state` value that the Authorization Server returns when redirecting the User Agent back to the Client.

Example:

```text
state=RANDOM_UNPREDICTABLE_VALUE
```

The Client stores the expected value before sending the user away.

Conceptually:

```text
1. Client generates state

   state = RANDOM_VALUE

2. Client stores expected state

3. Browser goes to Authorization Server

4. Authorization Server redirects back

   callback?code=...&state=RANDOM_VALUE

5. Client compares:

   received state
          │
          ▼
   expected state?
          │
      ┌───┴───┐
      │       │
     Yes      No
      │       │
      ▼       ▼
   Continue   Reject
```

A common security use of `state` is correlating the authorization response with the request that initiated it and mitigating cross-site request forgery against the redirect/callback flow.

The value should be generated and handled securely by the Client.

---

# 6. The Complete Basic Request

Putting the common parameters together:

```text
GET https://authorization-server.example/authorize
    ?response_type=code
    &client_id=CLIENT_ID
    &redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback
    &scope=read%20write
    &state=RANDOM_VALUE
```

The browser follows the redirect:

```text
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ HTTP redirect
     ▼
┌──────────┐
│ Browser  │
└────┬─────┘
     │
     │ GET /authorize?... 
     ▼
┌──────────────────────┐
│ Authorization Server │
└──────────────────────┘
```

This browser-based redirection is a fundamental part of the authorization endpoint interaction.

---

# 7. Adding OpenID Connect

OAuth 2.0 alone does not define a standard identity layer for telling the Client who the End-User is.

OpenID Connect adds identity behavior on top of OAuth 2.0.

The key signal is the `openid` scope.

Example:

```text
scope=openid profile email
```

Conceptually:

```text
scope contains "openid"
          │
          ▼
OpenID Connect request
          │
          ├── OAuth authorization behavior
          │
          └── OIDC identity behavior
```

OpenID Connect Core specifies that an authentication request is an OAuth 2.0 authorization request with additional OIDC requirements.

---

# 8. OIDC `nonce`

When using OpenID Connect, a Client can send a `nonce` parameter.

Example:

```text
nonce=ANOTHER_RANDOM_UNPREDICTABLE_VALUE
```

The OpenID Provider can include the nonce value in the resulting ID Token so the Client can verify that the token is associated with the authentication request it initiated.

Conceptually:

```text
Client
 │
 │ nonce = N123
 ▼
Authorization Request
 │
 ▼
OpenID Provider
 │
 ▼
ID Token

nonce = N123
```

The Client checks that the returned value matches its expected value.

`state` and `nonce` solve different correlation problems and should not automatically be treated as interchangeable.

We will examine them in more detail in later security lectures.

---

# 9. PKCE Begins With the Authorization Request

Proof Key for Code Exchange (PKCE) strengthens the Authorization Code flow, especially for public clients.

Before the authorization request, the Client generates a high-entropy secret called a:

```text
code_verifier
```

The Client derives a:

```text
code_challenge
```

and sends the challenge in the authorization request.

Example:

```text
code_challenge=DERIVED_VALUE
code_challenge_method=S256
```

Conceptually:

```text
Client
 │
 │ Generate secret
 │
 ├── code_verifier  ─────────── keep locally
 │
 └── code_challenge ─────────── send to /authorize
                                    │
                                    ▼
                           Authorization Server
```

Later, when exchanging the authorization code, the Client sends the original `code_verifier`.

The Authorization Server verifies that it corresponds to the earlier `code_challenge`.

```text
Authorization Request:

code_challenge
       │
       ▼
Authorization Code
       │
       ▼
Token Request:

code_verifier
       │
       ▼
Server verifies relationship
```

PKCE is defined in RFC 7636.

---

# 10. What the Authorization Server Must Validate

The Authorization Server should not simply trust arbitrary query parameters.

A conceptual validation process is:

```text
Authorization Request
        │
        ▼
┌────────────────────────────┐
│ Validate Client            │
├────────────────────────────┤
│ Is client_id recognized?   │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│ Validate redirect_uri      │
├────────────────────────────┤
│ Is it valid for this       │
│ registered Client?         │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│ Validate requested response│
│ type / flow                │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│ Evaluate requested scopes  │
└──────────────┬─────────────┘
               │
               ▼
        Continue / Reject
```

The exact validation rules and error behavior depend on the applicable specifications and provider implementation.

---

# 11. Why Changing a URL Parameter Does Not Create Permission

Suppose an attacker changes:

```text
scope=profile
```

to:

```text
scope=profile admin delete_everything
```

The request is only a request.

The attacker does not gain authority merely by writing more words into the URL.

The Authorization Server controls what authorization is actually granted.

```text
Client requests scopes
        │
        ▼
"profile admin delete_everything"
        │
        ▼
Authorization Server
        │
        ├── Is Client allowed to request this?
        ├── Is the resource / scope valid?
        ├── Has required authorization / consent occurred?
        └── Do policy rules allow it?
                │
                ▼
        Actual authorization result
```

This is an important trust boundary.

---

# 12. Microsoft Entra ID Mapping

For Microsoft Entra ID, your application is registered as a Client application.

The provider gives the application configuration information needed to construct and validate the flow.

At a high level:

```text
Your Application
      │
      │ client_id
      │ redirect_uri
      │ scopes
      │ state
      │ nonce / PKCE where applicable
      ▼
Microsoft Entra Authorization Endpoint
      │
      │ User authentication
      │ Authorization processing
      ▼
Your Redirect URI
      │
      │ code + state
      ▼
Your Application
```

The exact Microsoft endpoint and parameters should be taken from Microsoft Entra documentation or OpenID Connect discovery metadata rather than hard-coded from an unrelated provider example.

---

# 13. A Concrete Lab-Oriented Example

A conceptual OIDC Authorization Code + PKCE request might contain:

```text
response_type=code
client_id=YOUR_CLIENT_ID
redirect_uri=http://localhost:8000/auth/callback
scope=openid profile email
state=RANDOM_STATE
nonce=RANDOM_NONCE
code_challenge=PKCE_CHALLENGE
code_challenge_method=S256
```

Read this as:

```text
response_type=code
    → I want an authorization code.

client_id=...
    → This identifies my registered application.

redirect_uri=...
    → Return the response to this registered callback.

scope=openid profile email
    → Start OIDC and request these identity-related scopes.

state=...
    → Correlate this response with the request I started.

nonce=...
    → Bind OIDC token processing to this authentication request.

code_challenge=...
    → Prepare PKCE protection for the later token exchange.
```

---

# 14. Security Boundaries to Remember

## 14.1 Do not treat `client_id` as a password

```text
client_id
    = identifier

client_secret
    = credential for applicable confidential-client authentication
```

A `client_id` can appear in browser-visible requests.

---

## 14.2 Protect the redirect URI configuration

The Authorization Server must not redirect sensitive authorization responses to arbitrary attacker-controlled locations.

---

## 14.3 Use unpredictable correlation values

Values such as `state`, and where applicable OIDC `nonce`, should be generated and validated securely.

---

## 14.4 Use PKCE for Authorization Code flows as required or recommended by your client type and provider guidance

PKCE helps protect the authorization code exchange by binding the authorization request to the later token request.

---

## 14.5 Validate the response, not only the request

Receiving a `code` parameter does not mean the Client should blindly trust everything around it.

The Client must validate expected state and then perform the token exchange according to the protocol and provider requirements.

---

# 15. Common Misconceptions

## Misconception 1

> "The authorization request authenticates the user."

Not by itself.

The request starts an interaction with the Authorization Server, which may authenticate the user as part of the flow.

---

## Misconception 2

> "If I know the client_id, I can impersonate the application."

Not necessarily.

A `client_id` identifies the Client but is not itself proof of possession of a secret or authority to impersonate a confidential client.

---

## Misconception 3

> "I can edit scope in the URL to gain more permissions."

No.

The Authorization Server determines what can actually be granted and what is represented in the resulting authorization artifacts.

---

## Misconception 4

> "The redirect_uri is just a convenience setting."

No.

It is a major security boundary because authorization responses can contain security-sensitive values such as authorization codes.

---

# 16. Key Takeaways

```text
Authorization Request
        │
        ▼
Starts the authorization interaction
        │
        ▼
Client redirects User Agent
        │
        ▼
Authorization Server
        │
        ├── Validates request
        ├── Authenticates user when needed
        ├── Processes authorization
        └── Returns authorization response
```

The most important parameters are:

| Parameter | Purpose |
|---|---|
| `response_type` | Indicates the expected authorization response type |
| `client_id` | Identifies the registered Client |
| `redirect_uri` | Specifies the registered callback destination |
| `scope` | Requests access / OIDC scopes |
| `state` | Correlates request and response and can mitigate CSRF |
| `nonce` | OIDC value used to associate token processing with the request |
| `code_challenge` | PKCE value sent before the token exchange |
| `code_challenge_method` | Indicates how the PKCE challenge was derived |

The next major step is:

```text
Authorization Request
        │
        ▼
User / Authorization Server Interaction
        │
        ▼
Authorization Response
        │
        ▼
Authorization Code
```

---

# 17. Knowledge Check

### Question 1

What does `client_id` do?

```text
Answer:
It identifies the registered Client to the Authorization Server.
It is not, by itself, a secret.
```

### Question 2

Why is `redirect_uri` security-sensitive?

```text
Answer:
Because the authorization response may be delivered there.
The Authorization Server must apply appropriate validation against the
Client's registered configuration.
```

### Question 3

Can a Client gain additional permission simply by modifying `scope` in the URL?

```text
Answer:
No.
The Authorization Server evaluates and controls what authorization is granted.
```

### Question 4

What does `state` help the Client do?

```text
Answer:
Correlate the authorization response with the request that initiated it,
and it is commonly used to mitigate CSRF in the redirect flow.
```

### Question 5

What does adding `openid` to the scope indicate?

```text
Answer:
The request is invoking OpenID Connect behavior on top of OAuth 2.0.
```

### Question 6

What does PKCE add to the authorization request?

```text
Answer:
A code_challenge, which is later verified against the code_verifier during
the token exchange.
```

---

# 18. References

This lecture uses protocol standards and official documentation as its primary sources.

## 18.1 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

Defines the OAuth 2.0 authorization framework, including the authorization endpoint, authorization request, `response_type`, `client_id`, redirect URI behavior, scope, and state.

Source:

https://www.rfc-editor.org/rfc/rfc6749

Relevant areas:

```text
Section 3.1  — Authorization Endpoint
Section 4.1  — Authorization Code Grant
Section 4.1.1 — Authorization Request
Section 10.12 — Cross-Site Request Forgery
```

---

## 18.2 IETF RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

Defines PKCE, including the `code_verifier`, `code_challenge`, and `code_challenge_method` parameters.

Source:

https://www.rfc-editor.org/rfc/rfc7636

---

## 18.3 OpenID Connect Core 1.0

Defines OpenID Connect authentication requests and parameters including the `openid` scope and `nonce`.

Source:

https://openid.net/specs/openid-connect-core-1_0.html

Relevant areas:

```text
Section 3.1 — Authorization Code Flow
Section 3.1.2.1 — Authentication Request
```

---

## 18.4 OAuth 2.0 Security Best Current Practice — RFC 9700

Provides updated security guidance for OAuth 2.0 deployments, including redirect URI and authorization request security considerations.

Source:

https://www.rfc-editor.org/rfc/rfc9700

---

## 18.5 Microsoft Identity Platform — Authorization Code Flow

Microsoft's official documentation describing how the OAuth 2.0 authorization code flow is implemented by the Microsoft identity platform.

Source:

https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow

---

# 19. Source Hierarchy Used in This Lecture

```text
Protocol Standards
      │
      ├── IETF RFC 6749
      ├── IETF RFC 7636
      ├── IETF RFC 9700
      └── OpenID Connect Core
                │
                ▼
       Provider Documentation
                │
                ▼
       Microsoft Entra ID
```

For this lab:

> **Use protocol standards to understand the general security model, and use Microsoft documentation to understand the provider-specific implementation.**

---

# 20. Next Lecture

Continue to:

```text
docs/02-oauth-flow/02-authorization-code.md
```

The next lecture will answer:

```text
What exactly is an authorization code?

Why does the Authorization Server return a code instead of immediately
placing a long-lived credential in the front channel?

How is the code related to the Client and redirect URI?

Why can the code be exchanged only under the expected conditions?

How does PKCE protect the code exchange?
```
