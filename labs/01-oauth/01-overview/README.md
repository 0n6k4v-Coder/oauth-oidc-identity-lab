# Lab 01 — OAuth 2.0 Overview

> **Learning Track:** OAuth 2.0 & OpenID Connect Identity Lab  
> **Lab Type:** Production-oriented Foundation Lab  
> **Prerequisite:** Lecture 01 — OAuth 2.0 Overview

## Objective

Build the initial application boundary for the OAuth 2.0 learning track and identify the four OAuth roles in a real application architecture.

## Lab Model

This lab is a self-contained snapshot.

```text
Browser / User Agent
        ↓
      Client
        ↓
 Resource Server
```

The Authorization Server remains an external protocol participant and will be integrated in later labs.

## Expected Outcome

At the end of this lab, the repository should contain a runnable Client application and Resource Server with a clearly identified protected-resource boundary, without using fake OAuth tokens or fake authentication.

## Structure

Source code for this lab belongs inside this directory. If a later lab continues from this lab, that later lab must contain the complete implementation from this snapshot plus its new changes.

```text
01-overview/
├── README.md
└── src/
    ├── client/
    └── resource-server/
```

## Production-Oriented Requirements

- Keep Client and Resource Server responsibilities separate.
- Use configuration rather than hard-coding future provider settings.
- Implement explicit error handling.
- Do not log credentials or tokens.
- Do not introduce fake Access Token validation merely to demonstrate OAuth.
- Keep the implementation suitable for extension by later OAuth labs.

## Completion Criteria

- [ ] Client application exists and runs.
- [ ] Resource Server exists and runs.
- [ ] Protected-resource endpoint exists.
- [ ] OAuth roles are documented.
- [ ] Client and Resource Server boundaries are explicit.
- [ ] No fake authentication or token mechanism is used.
- [ ] The lab can run independently from later labs.
