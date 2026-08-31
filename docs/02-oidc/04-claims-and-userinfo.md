# Claims and UserInfo

## Learning Objective

By the end of this lecture, you should be able to:

- Explain what an OpenID Connect **Claim** represents.
- Distinguish **ID Token Claims** from **UserInfo Claims**.
- Understand how standard Claims are requested with OAuth 2.0 `scope` values.
- Explain the role of the **UserInfo Endpoint** and its Access Token.
- Recognize why `sub` is the key identifier for correlating an End-User across OIDC responses.

---

## 1. What Is a Claim?

A **Claim** is a piece of information asserted about a subject, represented as a name/value pair.

In OpenID Connect, Claims communicate information about the End-User and the authentication event. They may be returned in the **ID Token** or through the **UserInfo Endpoint**.

```text
OpenID Connect
      │
      └── Claims
           │
           ├── Identity / profile information
           ├── Contact information
           └── Authentication-related information
```

A Claim is therefore **information carried by the protocol**, not a separate token type.

---

## 2. Standard OpenID Connect Claims

OpenID Connect Core defines a standard set of Claims so that different Providers and Clients can use common names and semantics. These Claims may be returned in the ID Token or UserInfo Response. citeturn1search0

| Claim | Meaning | Typical category |
|---|---|---|
| `sub` | Stable identifier for the End-User at the Issuer | Identity |
| `name` | End-User's full displayable name | Profile |
| `given_name` | Given/first name(s) | Profile |
| `family_name` | Family name(s) | Profile |
| `preferred_username` | Preferred username | Profile |
| `picture` | URL of a profile picture | Profile |
| `email` | Preferred e-mail address | Contact |
| `email_verified` | Whether the e-mail address has been verified | Contact |
| `phone_number` | Preferred telephone number | Contact |
| `phone_number_verified` | Whether the phone number has been verified | Contact |
| `address` | Preferred postal address | Contact |
| `birthdate` | End-User's birthday | Profile |
| `locale` | End-User's locale | Profile |
| `zoneinfo` | End-User's time zone | Profile |
| `updated_at` | Time the End-User information was last updated | Profile |

The complete standard Claim definitions are specified by OpenID Connect Core; the table above intentionally highlights the Claims most useful for understanding the protocol flow rather than reproducing the entire specification. citeturn1search0

> **Important:** `email` is not defined as a unique identifier. Applications should use the OIDC subject identifier (`sub`) when correlating an End-User with the Issuer.

---

## 3. `sub`: The Core User Identifier

The `sub` Claim identifies the End-User at the Issuer.

```text
Issuer A
  │
  └── sub = "user-123"

Issuer B
  │
  └── sub = "user-987"
```

The identifier is scoped to the Issuer. A Client must therefore consider the combination of the **Issuer** and `sub` when identifying an End-User.

This distinction matters because two different OpenID Providers may use the same textual identifier for different people, while the same Provider can use different identifier strategies depending on its subject identifier configuration. OpenID Connect also defines pairwise subject identifiers for privacy-preserving correlation.

---

## 4. Requesting Claims with Scopes

OpenID Connect defines standard scope values that request groups of Claims.

| Scope | Claims requested |
|---|---|
| `openid` | Requests OpenID Connect authentication; it is the scope that distinguishes an OIDC request from a plain OAuth request. |
| `profile` | Default profile Claims such as `name`, `given_name`, `family_name`, `nickname`, `preferred_username`, `profile`, `picture`, `website`, `gender`, `birthdate`, `zoneinfo`, `locale`, and `updated_at` |
| `email` | `email`, `email_verified` |
| `address` | `address` |
| `phone` | `phone_number`, `phone_number_verified` |

These scope values are defined by OpenID Connect Core. The `profile`, `email`, `address`, and `phone` Claims are treated as voluntary Claims: requesting a scope does not mean the Client is guaranteed to receive every corresponding Claim.

For example:

```text
scope=openid profile email
```

means, conceptually:

```text
Authenticate the End-User
        +
Request standard profile information
        +
Request e-mail information
```

The actual Claims returned depend on what the OpenID Provider supports and is permitted to disclose.

---

## 5. Where Can Claims Be Returned?

OpenID Connect provides two important locations for Claims in the normal Authorization Code flow:

```text
                    OpenID Provider
                          │
             ┌────────────┴────────────┐
             │                         │
         ID Token                  UserInfo
             │                         │
       JWT Claims Set             JSON Claims
             │                         │
             └────────────┬────────────┘
                          │
                       Client
```

### ID Token

The ID Token is a security token defined by OpenID Connect. It contains Claims about the authentication and the authenticated End-User. The Client validates the ID Token according to the OIDC rules before relying on its Claims.

The ID Token is therefore part of the **authentication result**.

### UserInfo

The UserInfo Endpoint is an OAuth 2.0 Protected Resource that returns Claims about the authenticated End-User. The Client calls it using an Access Token obtained through the OIDC authentication flow. citeturn1search0

The UserInfo response is normally a JSON object containing Claim name/value pairs. Communication with the UserInfo Endpoint must use TLS.

---

## 6. ID Token vs UserInfo

| Aspect | ID Token | UserInfo |
|---|---|---|
| Protocol role | Authentication result | Protected user-information resource |
| Representation | JWT | JSON response |
| Obtained | From the Token Endpoint in applicable flows | By calling the UserInfo Endpoint |
| Authorization | Validated as an OIDC ID Token | Access controlled by an OAuth Access Token |
| Typical purpose | Establish and verify the authentication result | Obtain user attributes |
| Main protocol concern | Token validation and authentication claims | Protected-resource access and response validation |

The distinction is important: **an Access Token is not an ID Token, and UserInfo is not simply another representation of the ID Token.** They serve different protocol roles.

---

## 7. UserInfo Request

Once the Client has obtained an appropriate Access Token, it can call the UserInfo Endpoint.

```text
Client                         UserInfo Endpoint
  │                                  │
  │  GET /userinfo                  │
  │  Authorization: Bearer <AT>     │
  │ ────────────────────────────────>│
  │                                  │
  │       Claims about End-User      │
  │ <────────────────────────────────│
  │
```

The UserInfo Endpoint is a protected resource. The Access Token is therefore the credential used to authorize the request. OpenID Connect Core specifies support for the HTTP `GET` and `POST` methods and requires TLS for communication.

---

## 8. `sub` Must Match the Client's User Identity

A successful UserInfo Response contains the `sub` Claim. The Client uses it to associate the response with the End-User identified by the OIDC authentication result.

Conceptually:

```text
ID Token
{
  "iss": "https://issuer.example.com",
  "sub": "user-123"
}

             │
             │ same End-User
             ▼

UserInfo
{
  "sub": "user-123",
  "name": "Example User",
  "email": "user@example.com"
}
```

The Client must not blindly treat arbitrary UserInfo data as belonging to the authenticated user. OIDC defines UserInfo Response validation rules, including validation of the `sub` value against the subject identifier obtained during the authentication flow.

---

## 9. Claims Are Not All the Same Kind of Data

A useful mental model is to separate Claims by what they communicate:

- **Identity:** `sub`
- **Profile:** `name`, `given_name`, `family_name`, `picture`, `locale`
- **Contact:** `email`, `phone_number`
- **Verification state:** `email_verified`, `phone_number_verified`
- **Authentication context:** Claims such as `auth_time` and `acr` are related to the authentication event rather than ordinary profile data. citeturn1search0

This distinction becomes important later when deciding **which information belongs in an ID Token, which should be obtained from UserInfo, and which should not be requested at all**.

---

## 10. Claims and Privacy

Claims can contain personal information. OpenID Connect therefore treats Claims as part of its privacy considerations.

The principle for this lab is simple:

```text
Need a Claim?
     │
     ├── Yes → Request only what the application needs
     │
     └── No  → Do not request it
```

Requesting `profile`, `email`, `address`, or `phone` expands the information that the Client is asking the Provider to make available. The Provider still controls what information is actually returned. OpenID Connect's privacy model explicitly discusses personally identifiable information, data-access monitoring, and correlation.

---

## 11. Important Boundary: Claims vs OAuth Access-Token Claims

Do not assume that every claim you encounter in an OAuth ecosystem is an OpenID Connect Claim returned to the Client.

For example, RFC 9068 defines a JWT Profile for OAuth 2.0 Access Tokens. Such a JWT may contain authorization-oriented information such as `scope`, `aud`, and `client_id`, but its purpose is to represent an OAuth access token for a protected resource.

```text
OIDC ID Token
    │
    └── Authentication / End-User identity context

OAuth Access Token
    │
    └── Authorization to access a protected resource

UserInfo Response
    │
    └── End-User Claims returned by the protected resource
```

The fact that all three may contain JSON-like Claims does **not** make them interchangeable.

---

## 12. What This Lecture Establishes

At this point, the model should be:

```text
OAuth 2.0
   │
   └── Authorization
          │
          └── Access Token
                 │
                 └── Protected Resource
                        │
                        └── UserInfo

OpenID Connect
   │
   └── Authentication + Identity
          │
          └── ID Token
                 │
                 └── Authentication / identity Claims
```

The important relationships are:

- **Claim** = a name/value assertion about a subject or relevant protocol context.
- **ID Token** = an OIDC security token carrying authentication and identity information.
- **UserInfo** = a protected resource that exposes Claims about the authenticated End-User.
- **Access Token** = the credential used to access the UserInfo protected resource.
- **`sub`** = the critical End-User identifier used to correlate identity information.
- **Scopes** = one standardized mechanism for requesting groups of user Claims.

The next part of the learning path can build on this foundation by examining how these Claims are carried, validated, and trusted in the ID Token and UserInfo response.

---

## References

1. OpenID Foundation — **OpenID Connect Core 1.0 incorporating errata set 2** (15 December 2023), especially Sections 2, 5, 5.1, 5.3, 5.4, 5.7, and 17. citeturn0search0turn1search0
2. OpenID Foundation — **OpenID Connect Specifications / Errata Corrections**, confirming the current Core errata status. citeturn0search8turn0search12
3. IETF — **RFC 7519: JSON Web Token (JWT)**. The RFC defines JWT Claims and notes subsequent updates including RFC 8725. citeturn0search14
4. IETF — **RFC 9068: JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens**. Used to distinguish OAuth access-token Claims from OIDC identity Claims. citeturn0search4

> **Scope note:** This lecture focuses on the Core OpenID Connect Claims model and UserInfo mechanism. Advanced Claims syntax, Identity Assurance, and Verifiable Credentials are intentionally outside this lecture and should be treated as separate extensions/topics rather than mixed into the Core model.
