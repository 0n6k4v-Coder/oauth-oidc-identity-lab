# Lecture 03 — Token Exchange

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Module:** OAuth / OIDC Flow  
> **Level:** Intermediate  
> **Prerequisite:** Authorization Request and Authorization Code

---

# 1. Learning Objectives

After completing this lecture, you should be able to:

- Explain what the Token Endpoint is.
- Explain why the Client exchanges an Authorization Code.
- Understand the structure of an OAuth Token Request.
- Understand how the Authorization Server validates a Token Request.
- Explain the role of `grant_type`.
- Explain the role of `code`.
- Explain the role of `redirect_uri`.
- Explain the role of `client_id`.
- Explain how PKCE participates in the Token Exchange.
- Distinguish public Clients from confidential Clients.
- Understand Client authentication at the Token Endpoint.
- Understand what an Access Token Response contains.
- Distinguish an Access Token, ID Token, and Refresh Token.
- Understand why the Token Endpoint is a critical security boundary.
- Connect the Token Exchange to Microsoft Entra ID.

---

# 2. Where We Are

The previous lecture ended here:

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

The Client now possesses an Authorization Code.

But the Client still does **not** have the Access Token.

The next step is:

```text
Client
   │
   │ Authorization Code
   ▼
Token Endpoint
   │
   │ Validate
   ▼
Tokens
```

This process is called the:

```text
Token Exchange
```

---

# 3. What Is the Token Endpoint?

The **Token Endpoint** is an endpoint exposed by the Authorization Server where the Client exchanges an authorization grant for an Access Token.

In the Authorization Code Grant:

```text
Authorization Code
        │
        ▼
   Token Endpoint
        │
        ▼
   Access Token
```

The Token Endpoint is therefore different from the Authorization Endpoint.

### Authorization Endpoint

Used primarily through the User Agent:

```text
Browser
   │
   ▼
Authorization Endpoint
```

It handles things such as:

```text
User Authentication
User Interaction
Authorization / Consent
```

### Token Endpoint

Used by the Client:

```text
Client
   │
   ▼
Token Endpoint
```

It handles:

```text
Authorization Code Exchange
Client Authentication
PKCE Verification
Token Issuance
```

---

# 4. Authorization Endpoint vs Token Endpoint

A useful mental model is:

```text
                 Authorization Server
                 ┌─────────────────────┐
                 │                     │
Browser ────────►│ Authorization      │
                 │ Endpoint            │
                 │                     │
                 └─────────────────────┘
                          │
                          │ Authorization Code
                          ▼
                 ┌─────────────────────┐
Client ─────────►│ Token Endpoint      │
                 │                     │
                 └─────────────────────┘
                          │
                          ▼
                       Tokens
```

The two endpoints perform different jobs.

```text
Authorization Endpoint
        ↓
Obtain authorization

Token Endpoint
        ↓
Exchange authorization grant for tokens
```

---

# 5. The Authorization Code Is Not Enough

Suppose the Client receives:

```text
code=ABC123
```

It cannot simply call the API:

```http
GET /api/profile

Authorization: Bearer ABC123
```

That is incorrect.

The Authorization Code is not the Resource Server credential.

Instead:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ▼
Access Token
        │
        ▼
Resource Server
```

The Access Token is the artifact that is subsequently presented to the Resource Server.

---

# 6. The Token Request

The OAuth 2.0 Authorization Code Grant defines a Token Request to the Token Endpoint.

Conceptually:

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=AUTHORIZATION_CODE
&redirect_uri=https://client.example.com/callback
```

Depending on the Client and Authorization Server configuration, additional information may be required.

For example:

```text
client_id
client_secret
code_verifier
```

The exact requirements depend on the Client type and authentication method.

RFC 6749 defines the Authorization Code Token Request, while RFC 7636 adds the `code_verifier` parameter when PKCE is used.

---

# 7. `grant_type`

The Token Request contains:

```text
grant_type=authorization_code
```

This tells the Authorization Server:

> "I am using the Authorization Code Grant."

Conceptually:

```text
grant_type
     │
     ▼
What type of authorization grant
is being exchanged?
```

For this lecture:

```text
grant_type=authorization_code
```

The Authorization Server can therefore process the request according to the Authorization Code Grant rules.

---

# 8. The `code` Parameter

The Client sends the Authorization Code:

```text
code=ABC123
```

This is the code previously returned by the Authorization Server.

The relationship is:

```text
Authorization Request
        │
        ▼
Authorization Server
        │
        ▼
Authorization Code
        │
        ▼
Client
        │
        │ code=ABC123
        ▼
Token Endpoint
```

The Authorization Server then determines whether the code is valid.

---

# 9. The `redirect_uri` Parameter

If the `redirect_uri` parameter was included in the Authorization Request, RFC 6749 requires the corresponding value in the Token Request to be identical.

Conceptually:

```text
Authorization Request

redirect_uri =
https://client.example.com/callback
```

Then:

```text
Token Request

redirect_uri =
https://client.example.com/callback
```

The Authorization Server compares them.

```text
Original URI
     │
     ▼
https://client.example.com/callback

        =

Token Request URI
     │
     ▼
https://client.example.com/callback

        │
        ▼
      Match
```

If they do not match:

```text
Authorization Server
        │
        ▼
       Reject
```

Modern OAuth security guidance recommends exact redirect URI matching, with a narrowly defined localhost exception for native applications.

---

# 10. Client Identity

The Authorization Server also needs to understand which Client is making the Token Request.

Conceptually:

```text
Client
  │
  │
  ├── client_id
  │
  ▼
Authorization Server
```

For example:

```text
client_id=123456789
```

The Authorization Server can then associate:

```text
Authorization Code
        │
        ▼
Client
        │
        ▼
Client ID
```

The Authorization Code should not be treated as a universally transferable credential.

---

# 11. Public vs Confidential Clients

OAuth distinguishes between different types of Clients.

The most important distinction for this lecture is:

```text
Public Client
        vs
Confidential Client
```

## Public Client

A Public Client cannot safely keep credentials confidential.

Examples can include:

```text
Mobile Application
Desktop Application
Browser-Based Application
```

An attacker may be able to inspect the application or its environment.

Therefore:

```text
Do NOT assume a client_secret
can remain secret.
```

---

## Confidential Client

A Confidential Client can protect its credentials.

A common example is:

```text
Server-Side Web Application
```

Conceptually:

```text
Browser
   │
   ▼
Your Web Server
   │
   │ Client Authentication
   ▼
Authorization Server
```

The secret remains on the server rather than being distributed to the user's browser.

---

# 12. Client Authentication

A confidential Client may authenticate to the Token Endpoint.

For example:

```text
Client
   │
   ├── client_id
   ├── client_secret
   └── authorization_code
   │
   ▼
Token Endpoint
```

The Authorization Server can verify:

```text
Is this really the registered Client?
```

This is different from authenticating the user.

Remember:

```text
User Authentication
        ≠
Client Authentication
```

The user may have authenticated earlier through the Authorization Endpoint.

The Client may authenticate separately at the Token Endpoint.

---

# 13. Two Different Identities

This is extremely important.

During the flow there can be two different entities whose identity matters:

```text
              Authorization Server
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      User Identity          Client Identity
          │                       │
          │                       │
    "Who is the user?"      "Which application?"
```

For example:

```text
User:
Alice

Client:
My Web Application
```

The Authorization Server may need to establish both:

```text
Alice was authenticated.
        +
This request belongs to My Web Application.
```

Only then can it safely process the token exchange.

---

# 14. PKCE Enters the Token Exchange

Now we reach one of the most important security mechanisms in the flow.

During the Authorization Request, the Client generated:

```text
code_verifier
```

Then derived:

```text
code_challenge
```

For `S256`:

```text
code_verifier
      │
      ▼
SHA-256
      │
      ▼
Base64URL
      │
      ▼
code_challenge
```

The Authorization Request contained:

```text
code_challenge=...
code_challenge_method=S256
```

The Authorization Server associates that challenge with the Authorization Code.

---

# 15. The Client Sends the Code Verifier

When exchanging the code, the Client sends:

```text
POST /token

grant_type=authorization_code
&code=ABC123
&redirect_uri=https://client.example.com/callback
&code_verifier=ORIGINAL_SECRET
```

The Authorization Server already knows:

```text
Authorization Code
        │
        ▼
code_challenge
```

The server receives:

```text
code_verifier
```

and calculates:

```text
SHA-256(code_verifier)
        │
        ▼
Base64URL
        │
        ▼
Calculated Challenge
```

Then:

```text
Calculated Challenge
        │
        │ compare
        ▼
Stored Challenge
```

RFC 7636 specifies this verification process.

---

# 16. PKCE Verification

The conceptual decision is:

```text
                 Token Request
                      │
                      ▼
                code_verifier
                      │
                      ▼
                 SHA-256
                      │
                      ▼
              Calculated Challenge
                      │
                      ▼
              Compare with stored
              code_challenge
                 │          │
              Match      Mismatch
                 │          │
                 ▼          ▼
              Continue     Reject
```

Therefore:

```text
Stolen Authorization Code
        +
Missing code_verifier
        ↓
Token Exchange fails
```

This is one of the major reasons PKCE is so important.

RFC 9700 currently requires Authorization Servers to support PKCE and recommends `S256` as the secure challenge method.

---

# 17. What Does the Authorization Server Validate?

A simplified validation process looks like this:

```text
                 Token Request
                      │
                      ▼
             ┌─────────────────┐
             │ Token Endpoint  │
             └────────┬────────┘
                      │
                      ▼
             Is grant_type valid?
                      │
                      ▼
             Is Client recognized?
                      │
                      ▼
             Is Client authentication
             valid when required?
                      │
                      ▼
             Is Authorization Code valid?
                      │
                      ▼
             Has Code expired?
                      │
                      ▼
             Has Code already been used?
                      │
                      ▼
             Is Code bound to this Client?
                      │
                      ▼
             Does redirect_uri match?
                      │
                      ▼
             Does PKCE verification succeed?
                      │
                      ▼
                 Issue Tokens
```

This is a conceptual model.

Actual validation behavior depends on the Authorization Server and protocol configuration.

---

# 18. What Happens When Validation Fails?

The Authorization Server should not simply issue tokens.

For example:

```text
Invalid Authorization Code
        ↓
invalid_grant
```

Or:

```text
Invalid Client Authentication
        ↓
invalid_client
```

Or:

```text
Invalid Request
        ↓
invalid_request
```

OAuth defines standardized error responses for Token Endpoint failures.

The important security principle is:

```text
Validation Failure
       ↓
No Token
```

---

# 19. Successful Token Response

If validation succeeds, the Authorization Server returns a Token Response.

A conceptual response might look like:

```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "..."
}
```

For OpenID Connect, an ID Token may also be returned:

```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "id_token": "eyJ..."
}
```

The exact response depends on the requested protocol, scopes, Client configuration, and Authorization Server behavior.

---

# 20. `access_token`

The `access_token` is the credential that the Client can use to access protected resources according to the token's permissions and the Resource Server's validation rules.

Conceptually:

```text
Client
   │
   │ Authorization: Bearer ACCESS_TOKEN
   ▼
Resource Server
```

The Access Token is not necessarily a JWT.

It can be:

```text
JWT
```

or:

```text
Opaque Token
```

The OAuth specification does not require JWT as the Access Token format.

---

# 21. `token_type`

A Token Response can contain:

```text
token_type
```

For example:

```json
{
  "token_type": "Bearer"
}
```

This tells the Client how the Access Token is intended to be used.

With a Bearer token:

```http
Authorization: Bearer ACCESS_TOKEN
```

The Resource Server then applies its token validation and authorization rules.

---

# 22. `expires_in`

The response may contain:

```text
expires_in
```

For example:

```json
{
  "expires_in": 3600
}
```

Conceptually:

```text
Access Token
     │
     ├── Issued
     │
     ├── Valid
     │
     └── Expires
```

A Client should not assume that an Access Token is valid forever.

---

# 23. Refresh Token

A Token Response may also contain:

```text
refresh_token
```

A Refresh Token has a different purpose:

```text
Refresh Token
      │
      ▼
Token Endpoint
      │
      ▼
New Access Token
```

It is not normally sent to the Resource Server.

Compare:

```text
Access Token
     ↓
Resource Server
```

versus:

```text
Refresh Token
     ↓
Token Endpoint
```

Whether a Refresh Token is issued depends on the Authorization Server, client type, requested scopes, and policy.

---

# 24. ID Token

If this is an OpenID Connect flow, the Token Response may contain:

```text
id_token
```

The ID Token serves a different purpose from the Access Token.

```text
ID Token
   ↓
Client
   ↓
Authentication / Identity Information
```

while:

```text
Access Token
   ↓
Resource Server
   ↓
Protected Resource Access
```

Therefore:

```text
ID Token
    ≠
Access Token
```

---

# 25. The Complete Token Exchange

Putting everything together:

```text
                 Client
                    │
                    │ Authorization Code
                    │ code_verifier
                    ▼
             ┌───────────────┐
             │ Token Endpoint│
             └───────┬───────┘
                     │
                     ▼
              Validate Request
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     Client        Code         PKCE
     Auth          Check        Check
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
                All Valid?
                  │     │
                Yes      No
                 │        │
                 ▼        ▼
             Issue       Reject
             Tokens      Request
```

---

# 26. Full OAuth Authorization Code Flow

Now we can see the entire flow.

```text
┌──────────────┐
│     User     │
└──────┬───────┘
       │
       │ interacts with
       ▼
┌──────────────┐
│ User Agent   │
│   Browser    │
└──────┬───────┘
       │
       │ Authorization Request
       ▼
┌──────────────────────┐
│ Authorization Server │
│                      │
│ /authorize           │
└──────────┬───────────┘
           │
           │ Authenticate
           │ Authorize
           ▼
     Authorization Code
           │
           │ Redirect
           ▼
     ┌──────────────┐
     │    Client    │
     └──────┬───────┘
            │
            │ Token Request
            │ code
            │ code_verifier
            ▼
     ┌──────────────────────┐
     │ Authorization Server │
     │                      │
     │ /token               │
     └──────────┬───────────┘
                │
                │ Validate
                ▼
              Tokens
                │
        ┌───────┴────────┐
        ▼                ▼
 Access Token         ID Token
        │
        ▼
 Resource Server
```

---

# 27. Microsoft Entra ID

Microsoft Entra ID implements the Authorization Code Flow through the Microsoft identity platform.

Microsoft's official documentation describes the flow as:

```text
/authorize
    ↓
Authorization Code
    ↓
/token
    ↓
Access Token
```

Microsoft also recommends using the Authorization Code Flow together with PKCE and OpenID Connect for supported application types.

A simplified Microsoft Entra flow is:

```text
Your Application
       │
       │ /authorize
       ▼
Microsoft Entra ID
       │
       │ User Authentication
       │ Consent
       ▼
Authorization Code
       │
       │ Browser Redirect
       ▼
Your Callback
       │
       │ /token
       │
       │ code
       │ code_verifier
       ▼
Microsoft Entra ID
       │
       ▼
Token Response
```

---

# 28. Microsoft Entra Token Request

A conceptual Microsoft identity platform Token Request is:

```http
POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token

Content-Type: application/x-www-form-urlencoded

client_id=CLIENT_ID
&grant_type=authorization_code
&code=AUTHORIZATION_CODE
&redirect_uri=REDIRECT_URI
&code_verifier=CODE_VERIFIER
&client_secret=CLIENT_SECRET
```

The exact parameters depend on the application type.

For example:

```text
Confidential Web Application
        │
        └── may authenticate with client credentials

Public Client
        │
        └── must not rely on a client secret
```

Microsoft specifically states that public clients such as native applications and SPAs must not use client secrets or certificates to redeem authorization codes.

---

# 29. The Security Boundary

The Token Endpoint is a critical security boundary.

Think about what happens if an attacker can successfully exchange an Authorization Code:

```text
Authorization Code
        │
        ▼
Token Endpoint
        │
        ▼
Access Token
        │
        ▼
Protected API
```

Therefore the Token Endpoint must carefully validate:

```text
Client
Code
Redirect URI
PKCE
Expiration
Single-use state
Grant type
Authentication
```

The security of the entire OAuth flow depends on these relationships being correctly enforced.

---

# 30. A Practical Attack Scenario

Suppose an attacker obtains:

```text
Authorization Code = ABC123
```

They attempt:

```http
POST /token

grant_type=authorization_code
&code=ABC123
```

The Authorization Server should not simply say:

```text
"Code exists → Issue Token"
```

Instead:

```text
Code
 │
 ├── Valid?
 ├── Expired?
 ├── Already used?
 ├── Correct Client?
 ├── Correct redirect_uri?
 ├── Correct PKCE verifier?
 └── Client authentication valid?
```

Only after the required checks succeed:

```text
                Valid
                  │
                  ▼
              Issue Token
```

This is the core security model of the Token Exchange.

---

# 31. Why PKCE Matters So Much

Imagine:

```text
Attacker
   │
   │ steals Authorization Code
   ▼
ABC123
```

Without appropriate protections, the attacker may attempt:

```text
ABC123
   │
   ▼
Token Endpoint
```

With PKCE:

```text
ABC123
   │
   ├── Associated with code_challenge
   │
   ▼
Token Endpoint
   │
   │ requires
   ▼
code_verifier
```

The attacker has:

```text
Authorization Code
```

but does not have:

```text
code_verifier
```

Therefore:

```text
PKCE verification
       ↓
     FAIL
       ↓
   No Token
```

RFC 9700 specifically recommends PKCE for confidential clients and requires it for public clients as part of current OAuth security best practice.

---

# 32. Important Concept: The Client Does Not "Decode" the Authorization Code

A common beginner mistake is thinking:

```text
Authorization Code
       ↓
Decode
       ↓
User ID
```

That is not how the protocol should be understood.

The Authorization Code should be treated as:

```text
Opaque Value
```

The Client does not need to know:

```text
Who is inside the code?
What does the code contain?
How was the code generated?
```

Instead:

```text
Client
   │
   │ "Here is the code."
   ▼
Authorization Server
   │
   │ "I recognize and validate it."
   ▼
Tokens
```

This is an important architectural principle.

---

# 33. Token Exchange Mental Model

Think of the Authorization Code as a **temporary receipt**.

```text
Authorization Server
        │
        │ "Authorization completed."
        ▼
Authorization Code
        │
        ▼
Client
        │
        │ "I have the receipt."
        ▼
Token Endpoint
        │
        │ Verify receipt
        ▼
Tokens
```

But remember:

> The Authorization Code is a protocol credential, not literally a human-readable receipt.

It is intentionally opaque to the Client.

---

# 34. Key Takeaways

The most important concepts from this lecture are:

```text
Authorization Code
        ↓
Sent to Token Endpoint
        ↓
Token Request
        ↓
Authorization Server validates
        ↓
PKCE verification
        ↓
Client authentication when applicable
        ↓
Authorization Code validation
        ↓
Token Response
```

And:

```text
Authorization Code
        ≠
Access Token
```

```text
Access Token
        ≠
ID Token
```

```text
ID Token
        ≠
Refresh Token
```

Each artifact has a different purpose.

---

# 35. Knowledge Check

Before moving forward, you should be able to answer:

### Question 1

What is the Token Endpoint?

```text
Answer:

The Authorization Server endpoint where the Client exchanges an authorization grant,
such as an Authorization Code, for tokens.
```

### Question 2

Does the Client send the Authorization Code directly to the Resource Server?

```text
Answer:

No.

The Authorization Code is exchanged at the Token Endpoint.
```

### Question 3

What does `grant_type=authorization_code` mean?

```text
Answer:

It tells the Authorization Server that the Client is exchanging
an Authorization Code using the Authorization Code Grant.
```

### Question 4

Why is `redirect_uri` important?

```text
Answer:

It binds the Token Request to the redirect URI used in the
authorization transaction when the parameter was included.
```

### Question 5

What does PKCE provide?

```text
Answer:

It binds the authorization request to the later token exchange
using a code_challenge and code_verifier.
```

### Question 6

Does every OAuth Access Token have to be a JWT?

```text
Answer:

No.

OAuth does not require Access Tokens to use JWT.
They can also be opaque values.
```

### Question 7

What is the difference between an Access Token and an ID Token?

```text
Answer:

An Access Token is intended for accessing protected resources.

An ID Token is an OpenID Connect artifact containing authentication
and identity claims intended for the Client.
```

### Question 8

Can a Public Client safely keep a client secret?

```text
Answer:

No.

A Public Client cannot reliably keep credentials confidential.
```

---

# 36. Lecture Completion Checklist

Before continuing, verify that you understand:

- [ ] Token Endpoint
- [ ] Token Request
- [ ] `grant_type`
- [ ] Authorization Code exchange
- [ ] `redirect_uri`
- [ ] Client identification
- [ ] Client authentication
- [ ] Public Client
- [ ] Confidential Client
- [ ] PKCE
- [ ] `code_verifier`
- [ ] `code_challenge`
- [ ] Token Response
- [ ] Access Token
- [ ] Refresh Token
- [ ] ID Token
- [ ] Token Endpoint validation
- [ ] Authorization Code replay protection

---

# 37. Next Lecture

Continue to:

```text
docs/02-oauth-flow/04-complete-flow.md
```

The next lecture will combine everything we have learned so far:

```text
Authorization Request
        ↓
User Authentication
        ↓
Authorization
        ↓
Authorization Code
        ↓
Token Exchange
        ↓
Access Token
        ↓
Resource Server
```

We will follow the **complete OAuth 2.0 Authorization Code Flow from beginning to end**, including the browser, Client, Authorization Server, Token Endpoint, Resource Server, PKCE, scopes, and tokens.

After that foundation is complete, the laboratory can move from protocol mechanics into the identity-specific part of OpenID Connect.

---

# 38. References

This lecture prioritizes standards and official documentation.

## 38.1 IETF RFC 6749 — The OAuth 2.0 Authorization Framework

Defines the OAuth 2.0 Authorization Code Grant, Token Endpoint, Access Token Request, Token Response, and OAuth error responses.

Source:

https://www.rfc-editor.org/rfc/rfc6749

Relevant sections:

```text
Section 1.3.1 — Authorization Code
Section 1.3.3 — Client Credentials
Section 2.1 — Client Types
Section 3.2 — Token Endpoint
Section 4.1 — Authorization Code Grant
Section 4.1.3 — Access Token Request
Section 4.1.4 — Access Token Response
Section 5.2 — Error Response
```

---

## 38.2 IETF RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients

Defines PKCE and the relationship between:

```text
code_verifier
code_challenge
code_challenge_method
```

Source:

https://www.rfc-editor.org/rfc/rfc7636

Relevant sections:

```text
Section 4.1 — Client Creates a Code Verifier
Section 4.2 — Client Creates a Code Challenge
Section 4.3 — Client Sends the Code Challenge
Section 4.5 — Client Sends Authorization Code and Code Verifier
Section 4.6 — Server Verifies Code Verifier
```

---

## 38.3 IETF RFC 9700 — Best Current Practice for OAuth 2.0 Security

Provides current OAuth security guidance and updates earlier OAuth security recommendations.

Important topics:

```text
PKCE
Authorization Code Injection
Authorization Code Replay
Redirect URI Protection
CSRF
Token Replay
Client Authentication
OAuth Security Best Practices
```

Source:

https://www.rfc-editor.org/rfc/rfc9700

Particularly relevant:

```text
Section 2.1.1 — Authorization Code Grant
Section 2.5 — Client Authentication
Section 4.5 — Authorization Code Injection
Section 4.7 — Cross-Site Request Forgery
```

---

## 38.4 OpenID Connect Core 1.0

Defines the OpenID Connect Authorization Code Flow and the ID Token.

Source:

https://openid.net/specs/openid-connect-core-1_0.html

Relevant sections:

```text
Section 3.1 — Authentication using the Authorization Code Flow
Section 3.1.2 — Authorization Endpoint
Section 3.1.3 — Token Endpoint
Section 3.1.3.6 — Successful Token Response
```

---

## 38.5 Microsoft — Microsoft Identity Platform Authorization Code Flow

Official Microsoft documentation explaining how Microsoft Entra ID implements the OAuth 2.0 Authorization Code Flow.

Source:

https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow

Relevant topics:

```text
Request an authorization code
Redeem a code for an access token
Use the access token
Refresh the access token
PKCE
Redirect URIs
Client authentication
Public vs confidential applications
```

---

# 39. Source Hierarchy

For this laboratory, use sources in this order:

```text
                    Standards
                       │
          ┌────────────┴────────────┐
          │                         │
        IETF                    OpenID Foundation
          │                         │
     RFC 6749                   OIDC Core
     RFC 7636
     RFC 9700
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
              Protocol Understanding
                       │
                       ▼
             Microsoft Documentation
                       │
                       ▼
              Microsoft Entra ID
                       │
                       ▼
                 Hands-on Lab
```

The principle is:

> **First understand what the protocol standard defines. Then understand how Microsoft Entra implements that protocol. Finally, verify the behavior yourself through the laboratory.**

This laboratory is designed around exactly that progression.
