# Lecture 02 — OAuth 2.0 Roles

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab
> **Level:** Foundation
> **Prerequisite:** Lecture 01 — OAuth 2.0 Overview

---

## 1. Learning Objectives

After completing this lecture, you should be able to:

* Identify the four OAuth 2.0 roles.
* Explain the responsibility of each role.
* Distinguish the Client from the Resource Owner.
* Distinguish the Authorization Server from the Resource Server.
* Explain why OAuth roles describe protocol responsibilities rather than necessarily separate machines.
* Understand how the roles interact during authorization and resource access.
* Understand how modern OAuth security guidance affects the responsibilities of Clients, Authorization Servers, and Resource Servers.
* Understand why browser-based and native applications are still Clients even though their deployment architectures differ.

---

# 2. Why OAuth Defines Roles

OAuth is easier to reason about when each participant has a clearly defined responsibility.

Instead of thinking:

```text
"The OAuth server does everything."
```

we should ask:

```text
Who wants access?

Who can authorize that access?

Who issues the Access Token?

Who protects the resource?
```

These questions lead directly to the four OAuth roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

RFC 6749 defines these four roles as the foundation of the OAuth protocol model.

---

# 3. The Four Roles at a Glance

The basic relationship is:

```text
             Resource Owner
                    │
                    │ Grants authorization
                    ▼
                  Client
                    │
                    │ Requests authorization
                    ▼
            Authorization Server
                    │
                    │ Access Token
                    ▼
             Resource Server
                    │
                    │ Protected Resource
                    ▼
                  Client
```

Each role answers a different question:

```text
Resource Owner
    ↓
"Who can authorize access?"

Client
    ↓
"Which application wants access?"

Authorization Server
    ↓
"Who issues the Access Token?"

Resource Server
    ↓
"Who protects the requested resource?"
```

This separation is one of the most important mental models in OAuth.

---

# 4. Resource Owner

The **Resource Owner** is the entity capable of granting access to a protected resource.

In a typical user-delegated scenario:

```text
Resource Owner
      =
User
```

For example:

```text
User
  │
  │ controls
  ▼
Private Data
```

The important part of the definition is the authority to grant access.

The Resource Owner is therefore not defined simply as:

```text
"the person using the application"
```

but as:

```text
"The entity capable of granting access
to the protected resource."
```

When the Resource Owner is a person, RFC 6749 refers to that person as an **end-user**.

---

# 5. Client

The **Client** is the application making protected-resource requests on behalf of the Resource Owner and with its authorization.

The word *client* describes a protocol role, not a particular kind of application.

It can be:

```text
Web Application
Mobile Application
Desktop Application
Browser-based JavaScript Application
Backend Application
```

RFC 6749 explicitly states that the term Client does not imply a particular implementation architecture or execution environment.

Therefore:

```text
Client
    ≠
Browser
```

and:

```text
Client
    ≠
Backend Server
```

automatically.

A Browser application can be the OAuth Client, while a backend application can also be an OAuth Client.

---

# 6. Client Does Not Mean Resource Owner

These roles are often confused.

Consider:

```text
User
  │
  │ owns / controls
  ▼
Protected Data

Web Application
  │
  │ requests access to
  ▼
Protected Data
```

The roles are:

```text
User
    = Resource Owner

Web Application
    = Client
```

The Client is asking for access.

The Resource Owner has the authority to grant it.

Therefore:

```text
Client ≠ Resource Owner
```

even when the Client is acting on behalf of that user.

---

# 7. Authorization Server

The **Authorization Server** is the server responsible for issuing Access Tokens to the Client after successfully processing the applicable authorization grant.

Conceptually:

```text
Authorization Server
        │
        ├── Authorization Endpoint
        │
        └── Token Endpoint
```

The Authorization Server is therefore responsible for the authorization side of the protocol.

In a user-delegated flow it may also authenticate the Resource Owner before obtaining authorization.

However, this does not mean:

```text
OAuth
    =
Authentication Protocol
```

Authentication and identity will be addressed later through OpenID Connect.

---

# 8. Resource Server

The **Resource Server** is the server hosting protected resources and capable of accepting protected-resource requests using Access Tokens.

For example:

```text
Protected API
```

The relationship is:

```text
Client
   │
   │ Access Token
   ▼
Resource Server
   │
   │ Authorization decision
   ▼
Protected Resource
```

The Resource Server therefore sits at the resource-access boundary.

Its fundamental question is:

```text
"May this request access this protected resource?"
```

The exact validation and authorization mechanism depends on the token and deployment architecture.

---

# 9. Authorization Server and Resource Server Are Different Roles

A common misconception is:

```text
Authorization Server
    =
Resource Server
```

They are not conceptually the same role.

The Authorization Server is responsible for issuing authorization credentials.

The Resource Server protects resources and evaluates requests using those credentials.

The relationship is:

```text
Authorization Server
        │
        │ Issues Access Token
        ▼
       Client
        │
        │ Presents Access Token
        ▼
Resource Server
```

RFC 6749 explicitly allows the Authorization Server and Resource Server to be operated by the same server or by separate entities.

The important distinction is therefore **responsibility**, not physical deployment.

---

# 10. One Platform Can Perform Multiple Roles

A real platform may combine roles.

For example:

```text
Identity Platform
    │
    ├── Authorization Service
    │
    └── API
```

The same platform may therefore act as:

```text
Authorization Server
        +
Resource Server
```

That does not collapse the two protocol roles into one concept.

It simply means:

```text
One deployment
    ↓
Multiple protocol responsibilities
```

This distinction becomes especially important when analyzing trust boundaries.

---

# 11. Client, Authorization Server, and Resource Server Are Independent Roles

Modern OAuth security guidance emphasizes that these parties should be reasoned about according to their protocol roles even when they are owned or operated by the same organization.

For browser-based applications, RFC 10017 explicitly notes that the Client, Authorization Server, and Resource Server are considered independent parties for the purposes of the OAuth architecture, regardless of whether they are owned or operated by the same entity.

Therefore:

```text
Same Company
    ≠
Same Protocol Role
```

and:

```text
Same Host
    ≠
Same Protocol Responsibility
```

---

# 12. The Roles Form a Trust Relationship

The roles are not merely labels.

They create a chain of security decisions:

```text
Resource Owner
      │
      │ Authorization decision
      ▼
Authorization Server
      │
      │ Access Token
      ▼
Client
      │
      │ Protected-resource request
      ▼
Resource Server
```

At each stage, a different party has a different responsibility.

For example:

```text
Authorization Server
    ↓
"Issued this authorization credential."

Client
    ↓
"Presents the credential to access the resource."

Resource Server
    ↓
"Determines whether this request is authorized."
```

This is why OAuth cannot be understood simply as:

```text
Client → Server → Token
```

The roles explain **who is responsible for what**.

---

# 13. The Client's Responsibility

The Client is not merely a passive receiver of tokens.

The Client has protocol and security responsibilities.

Depending on the deployment, the Client must correctly handle things such as:

```text
Authorization Requests
Redirect Responses
Authorization Codes
PKCE
Client Authentication
Access Tokens
Token Storage
CSRF Protection
Mix-Up Protection
```

Current OAuth Security BCP requires Clients to protect authorization flows against threats such as CSRF, authorization-code injection, and mix-up attacks.

The exact requirements depend on the Client type and deployment architecture.

---

# 14. The Authorization Server's Responsibility

The Authorization Server is responsible for protecting the authorization process and issuing tokens under appropriate conditions.

Modern security guidance places responsibilities on the Authorization Server such as:

```text
Protect redirect processing
Validate redirect URIs
Protect authorization codes
Support and enforce PKCE where required
Prevent open redirectors
Protect against authorization-code injection
Protect against phishing and related redirect attacks
```

For example, RFC 9700 requires exact redirect URI matching, except for the defined localhost native-app case, and requires public clients to use PKCE.

The Authorization Server therefore has responsibilities beyond simply:

```text
"Generate a token."
```

---

# 15. The Resource Server's Responsibility

The Resource Server is responsible for protecting the resource.

Its security boundary begins when the Client presents an Access Token.

Conceptually:

```text
Client
   │
   │ Access Token
   ▼
Resource Server
   │
   ├── Is this token valid?
   ├── Is it intended for this resource?
   ├── Does it grant the required privileges?
   └── Should this request be allowed?
```

Current OAuth Security BCP recommends restricting Access Tokens to the minimum privileges required and recommends audience restriction to a specific Resource Server, or a small set of Resource Servers where necessary. The Resource Server is responsible for refusing requests when the token is not intended for that resource.

Therefore:

```text
Token accepted
    ≠
Every request automatically authorized
```

The Resource Server still has an authorization decision to make.

---

# 16. Client Types

OAuth defines different categories of Clients based on their ability to maintain the confidentiality of credentials.

The two foundational categories are:

```text
Confidential Client
Public Client
```

A **confidential Client** can maintain the confidentiality of its authentication credentials.

A **public Client** cannot.

For example:

```text
Backend application
    ↓
May be able to protect client credentials
```

while:

```text
Browser application
    ↓
Code is delivered to the user
    ↓
Static secrets cannot be treated as confidential
```

RFC 6749 establishes this distinction, and RFC 10017 makes the consequence explicit for browser-based applications: code delivered to the user's browser is unsuitable for containing provisioned confidential secrets, so browser-based applications are typically public Clients.

---

# 17. Why Client Type Matters

The Client role is the same:

```text
Client
```

but its security capabilities can differ.

Compare:

```text
Confidential Client
        │
        └── Can protect client credentials
```

with:

```text
Public Client
        │
        └── Cannot keep a provisioned secret confidential
```

This distinction affects mechanisms such as:

```text
Client Authentication
PKCE
Token Handling
Deployment Architecture
```

Therefore:

```text
Same OAuth role
    ≠
Same security architecture
```

---

# 18. Browser-Based Application Example

A browser application may look like:

```text
User
  │
  ▼
Browser Application
  │
  │ OAuth Client
  ▼
Authorization Server
  │
  │ Access Token
  ▼
Browser Application
  │
  │ Protected Resource Request
  ▼
Resource Server
```

The browser application is still the **Client**.

The Browser is also the **User Agent** through which the Resource Owner interacts with the Authorization Server.

These are related concepts but should not be conflated:

```text
User Agent
    =
The software used by the user to interact

Client
    =
The OAuth application requesting authorization
```

RFC 10017 specifically addresses browser-based applications as OAuth Clients and their security architecture.

---

# 19. Native Application Example

A native application is also an OAuth Client.

Conceptually:

```text
User
  │
  ▼
Native Application
  │
  │ OAuth Client
  ▼
External User Agent
  │
  ▼
Authorization Server
```

RFC 8252 recommends that native applications use an external user-agent for authorization rather than embedding the authorization interaction inside the application.

The protocol role remains:

```text
Native Application
    =
Client
```

The deployment architecture changes, but the OAuth role does not.

---

# 20. Roles in a Real System

Suppose we have:

```text
My Application
Authentication Service
Protected API
```

A possible role mapping is:

```text
My Application
      ↓
Client

Authentication Service
      ↓
Authorization Server

Protected API
      ↓
Resource Server

Person using My Application
      ↓
Resource Owner
```

The important question is not:

```text
"What product name is this?"
```

but:

```text
"What OAuth role does this component perform?"
```

That distinction allows us to analyze different implementations using the same conceptual model.

---

# 21. One Authorization Server Can Serve Multiple Resource Servers

The relationship does not have to be one-to-one.

For example:

```text
                  Authorization Server
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
          API A        API B       API C
```

The Authorization Server can issue Access Tokens accepted by multiple Resource Servers.

RFC 6749 explicitly describes this possibility.

Modern OAuth security guidance therefore recommends paying attention to token audience and resource restriction.

A token should not be assumed to be valid for every Resource Server merely because it was issued by the same Authorization Server.

---

# 22. The Complete Responsibility Model

The roles can now be viewed as a responsibility map:

```text
Resource Owner
    │
    └── Grants authorization

Client
    │
    ├── Requests authorization
    ├── Exchanges grants for tokens
    └── Requests protected resources

Authorization Server
    │
    ├── Processes authorization
    └── Issues Access Tokens

Resource Server
    │
    ├── Protects resources
    ├── Evaluates Access Tokens
    └── Applies resource authorization
```

This is more useful than memorizing four definitions independently.

---

# 23. Security Boundaries Between Roles

A useful way to think about the architecture is:

```text
               AUTHORIZATION BOUNDARY
                         │
                         ▼
Resource Owner ──► Authorization Server
                         │
                         │ Token
                         ▼
                       Client
                         │
                         │ Access Token
                         ▼
                  Resource Server
                         │
                         ▼
                   Protected Data
```

Each transition represents a security boundary.

For example:

```text
Resource Owner → Authorization Server
```

asks:

```text
Has the user authorized access?
```

while:

```text
Client → Resource Server
```

asks:

```text
Does this credential authorize this resource request?
```

Those are different questions.

---

# 24. What Roles Do Not Tell You

The role model tells us **who is responsible for what**, but it does not by itself tell us:

```text
Which HTTP parameters are required
Which token format is used
How the Client authenticates
How PKCE works
How an ID Token is validated
How a provider implements the protocol
```

Those topics require additional specifications and later lectures.

This is intentional.

The role model should be established before studying the detailed protocol mechanics.

---

# 25. Practical Mental Model

Whenever you encounter an OAuth system, identify the participants using these questions:

```text
1. Who owns or controls the protected resource?

2. Which application wants to access it?

3. Which server authorizes the Client and issues tokens?

4. Which server protects the actual resource?
```

Then map them:

```text
Who authorizes?
    ↓
Resource Owner

Who requests?
    ↓
Client

Who issues?
    ↓
Authorization Server

Who protects?
    ↓
Resource Server
```

Once these four questions are clear, the rest of the OAuth protocol becomes easier to place.

---

# 26. Knowledge Check

### Question 1

What are the four OAuth 2.0 roles?

### Question 2

What makes an entity a Resource Owner?

### Question 3

What makes an application a Client?

### Question 4

Why does the term Client not imply a particular execution environment?

### Question 5

What is the primary responsibility of the Authorization Server?

### Question 6

What is the primary responsibility of the Resource Server?

### Question 7

Why can the Authorization Server and Resource Server be operated by the same physical system without becoming the same protocol role?

### Question 8

What is the difference between a Client and a Resource Owner?

### Question 9

What is the difference between a User Agent and an OAuth Client?

### Question 10

Why does Client type matter for security?

### Question 11

Why are browser-based applications generally treated as public Clients?

### Question 12

Why should an Access Token not automatically be assumed to be valid at every Resource Server?

---

# 27. Lecture Summary

OAuth 2.0 defines four primary roles:

```text
Resource Owner
Client
Authorization Server
Resource Server
```

Their responsibilities are:

```text
Resource Owner
    ↓
Can grant access

Client
    ↓
Requests and uses delegated authorization

Authorization Server
    ↓
Processes authorization and issues Access Tokens

Resource Server
    ↓
Protects resources and evaluates authorized requests
```

The most important distinctions are:

```text
Client
    ≠
Resource Owner

Authorization Server
    ≠
Resource Server

Client
    ≠
User Agent
```

A deployment can combine roles physically without combining their protocol responsibilities.

Modern OAuth security guidance also makes clear that the security responsibilities of these roles matter independently. Public Clients must use appropriate mechanisms such as PKCE, Authorization Servers must protect redirect-based flows and authorization grants, and Resource Servers should restrict token use to the intended resources and privileges.

The central mental model is:

```text
WHO?

Resource Owner
      ↓
grants authorization

Client
      ↓
requests access

Authorization Server
      ↓
issues Access Token

Resource Server
      ↓
protects Resource
```

Once you can identify these four roles in an unfamiliar system, you have the foundation required to understand the detailed OAuth protocol flow.

---

# 28. References

```text
RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Primary source for:
- Resource Owner
- Client
- Authorization Server
- Resource Server
- Authorization Grant
- Access Token
- Authorization / Token endpoints
- Confidential and public Clients


RFC 9700 — Best Current Practice for OAuth 2.0 Security
https://www.rfc-editor.org/rfc/rfc9700.html

Current general OAuth security guidance.

Relevant to this lecture:
- Client responsibilities
- Authorization Server responsibilities
- Resource Server responsibilities
- PKCE
- Redirect URI protection
- CSRF protection
- Authorization-code protection
- Mix-up protection
- Access-token privilege restriction
- Audience/resource restriction
- Client authentication


RFC 8252 — OAuth 2.0 for Native Apps
https://www.rfc-editor.org/rfc/rfc8252.html

Relevant to:
- Native applications as OAuth Clients
- External user-agent architecture
- Public native clients
- PKCE


RFC 10017 — OAuth 2.0 for Browser-Based Applications
https://www.rfc-editor.org/rfc/rfc10017.html

Current Best Current Practice for browser-based OAuth Clients.

Relevant to:
- Browser-based applications as Clients
- Public-client security
- Browser-specific threat model
- Client / Authorization Server / Resource Server relationships
- Modern browser deployment architecture


RFC 8414 — OAuth 2.0 Authorization Server Metadata
https://www.rfc-editor.org/rfc/rfc8414.html

Relevant to:
- Dynamic discovery of Authorization Server configuration
- Modern OAuth deployments with dynamically established relationships
```

---

# 29. Source Update Analysis

The foundational role definitions come from RFC 6749 and remain applicable.

The following newer specifications affect how those roles should be understood in modern deployments:

```text
RFC 6749
    ↓
Defines the four core OAuth roles
    │
    ├── Resource Owner
    ├── Client
    ├── Authorization Server
    └── Resource Server

RFC 9700
    ↓
Updates the security model around those roles
    │
    ├── Client security responsibilities
    ├── Authorization Server security responsibilities
    ├── Resource Server token restrictions
    ├── PKCE
    ├── redirect protection
    └── mix-up protection

RFC 8252
    ↓
Specializes Client architecture for native applications

RFC 10017
    ↓
Provides current security and architecture guidance
for browser-based Clients
```

These updates affect the lecture itself because they clarify that OAuth roles remain stable while **security responsibilities and deployment requirements have evolved**.

The role definitions should therefore be learned from RFC 6749, but the way those roles are implemented today must be interpreted together with the applicable modern Best Current Practice.

---

# 30. Lab Connection

The next practical stage will take these abstract roles and identify them in an actual OAuth deployment.

The Lab should answer:

```text
Which component is the Client?

Which component is the Authorization Server?

Which component is the Resource Server?

Where is the Resource Owner involved?

Which interactions cross the boundaries between these roles?
```

Later Labs will then implement and observe the protocol messages exchanged between them.
