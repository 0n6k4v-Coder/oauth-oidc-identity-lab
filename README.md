# OAuth 2.0 & OpenID Connect Identity Lab

A practical, standards-first learning laboratory for OAuth 2.0 and OpenID Connect.

## Learning Model

```text
Standards
   ↓
Core Theory
   ↓
Production-oriented Labs
   ↓
Provider Implementation
   ↓
Microsoft Entra ID
   ↓
Future Providers
```

## Repository Boundaries

```text
docs/
    What the standard means

labs/
    How we implement and verify it

providers/
    How a real provider implements the standard

app/
    The real application we gradually build

experiments/
    Inspection, negative testing, and security experiments
```

## Principles

- Core theory remains provider-neutral.
- Microsoft Entra ID is the first real provider track, not the definition of OAuth/OIDC.
- Labs are production-oriented implementations, not toy proof-of-concepts.
- Labs should observe, implement, validate, and test failure cases where appropriate.
- Standard sources are checked for applicable updates before new lecture content is written.
- The repository grows only as much as the learning objectives require.

## Learning Path

The exact number and structure of lectures are determined by the subject matter rather than a fixed section or lecture-count pattern.

The intended progression is:

```text
Understand
   ↓
Observe
   ↓
Implement
   ↓
Validate
   ↓
Break
   ↓
Explain
   ↓
Transfer to another Provider
```

## Initial Provider

The first provider-specific track is:

```text
Microsoft Entra ID
```

Additional providers can be added later without changing the provider-neutral theory.
