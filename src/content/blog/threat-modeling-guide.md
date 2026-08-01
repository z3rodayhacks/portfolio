---
title: "Practical Threat Modeling for Developers"
description: "A no-nonsense guide to threat modeling using STRIDE and attack trees, with worked examples for a typical SaaS application."
date: "2024-05-10"
tags: ["Threat Modeling", "STRIDE", "Secure Design", "AppSec"]
featured: false
draft: false
---

## Why Threat Modeling Matters

Security bugs are cheapest to fix in design, not production. Threat modeling forces you to think
adversarially before writing a single line of code.

The four key questions (per Microsoft's SDL):

1. **What are we building?** — System diagram
2. **What can go wrong?** — STRIDE analysis
3. **What are we doing about it?** — Mitigations
4. **Did we do a good job?** — Validation

## STRIDE in 5 Minutes

| Threat | Example | Mitigation |
|--------|---------|-----------|
| **S**poofing | Fake user identity | Authentication |
| **T**ampering | Modify database records | Integrity checks / MACs |
| **R**epudiation | Deny sending a message | Audit logging |
| **I**nformation Disclosure | Leak PII | Encryption, access control |
| **D**enial of Service | Flood API endpoints | Rate limiting |
| **E**levation of Privilege | User gains admin rights | Authorization checks |

## Worked Example: User Login Flow

```
[Browser] ──HTTPS──► [Load Balancer] ──► [Auth Service] ──► [User DB]
                                              │
                                              └──► [Session Store (Redis)]
```

### Apply STRIDE to Auth Service

**Spoofing**: Can someone impersonate the auth service?
- Mitigation: mTLS between internal services

**Tampering**: Can tokens be modified?
- Mitigation: HMAC-signed JWTs with short expiry

**Information Disclosure**: Can login responses leak user existence?
- Mitigation: Consistent timing responses; generic error messages

## Attack Trees

An attack tree for "Bypass authentication":

```
Bypass Auth
├── Steal valid credentials
│   ├── Phishing
│   ├── Credential stuffing
│   └── Password spray
├── Forge authentication token
│   ├── JWT algorithm confusion
│   └── Weak signing key
└── Session fixation
```

Each leaf becomes a test case in your security test suite.

## Tooling

- **OWASP Threat Dragon** — Free, visual threat modeling
- **Microsoft Threat Modeling Tool** — STRIDE-focused, Windows
- **Trike** — Risk-based approach
- **draw.io** — Simple diagrams with manual STRIDE annotation

## Takeaway

Spend 2 hours threat modeling before writing authentication code. You'll find more
vulnerabilities in those 2 hours than 2 weeks of penetration testing the finished product.
