# OAuth 2.0 Labs

Production-oriented, self-contained learning labs for the OAuth 2.0 track.

## Lab Model

Each lab is an isolated, reproducible snapshot of the implementation at that learning stage.

- A lab contains its own complete source code.
- A continuation lab includes the complete implementation it builds upon, plus its new changes.
- An independent lab contains only the implementation required for its own learning objective.
- Each lab should be runnable and understandable without relying on another lab's working tree.
- Labs are production-oriented and should focus on realistic implementation, security controls, validation, error handling, and tests rather than toy proof-of-concepts.

## Separation of Concerns

The labs demonstrate protocol concepts independently from provider-specific implementations.

```text
OAuth / OIDC Standard Concepts
        ↓
Provider-neutral Labs
        ↓
Provider-specific Experiments
```

Provider-specific work belongs under the provider area rather than being embedded into the provider-neutral OAuth labs.
