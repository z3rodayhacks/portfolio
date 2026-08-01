---
title: "Zero Trust Network Scanner"
description: "A comprehensive network scanner that identifies misconfigurations in zero-trust network architectures, detects lateral movement paths, and generates remediation reports."
date: "2024-09-15"
tags: ["Network Security", "Python", "Zero Trust", "Automation"]
thumbnail: "/images/projects/zt-scanner.png"
featured: true
github: "https://github.com/yourusername/zt-scanner"
status: "completed"
techStack: ["Python 3.11", "Scapy", "Nmap", "PostgreSQL", "Docker", "FastAPI"]
category: "Security Tooling"
---

## Overview

The Zero Trust Network Scanner automates the identification of trust relationship misconfigurations
in enterprise networks. It maps implicit trust paths between network segments that violate zero-trust
principles and prioritises remediation by risk score.

## Problem Statement

Many organisations claim to implement zero-trust architectures but retain implicit trust relationships
from legacy network designs. Manual auditing is time-consuming and error-prone at enterprise scale.

## Solution

The scanner performs:

1. **Topology Discovery** — Active and passive enumeration of network segments, subnets, and peering relationships
2. **Trust Analysis** — Identifies east-west communication paths that bypass micro-segmentation policies
3. **Risk Scoring** — CVSS-inspired scoring weighted by data classification and blast radius
4. **Report Generation** — Executive-level and technical PDF reports with specific remediation steps

## Technical Architecture

```python
# Example: Trust path analysis using graph traversal
from scanner.graph import NetworkGraph

graph = NetworkGraph.from_topology("topology.json")
violations = graph.find_trust_violations(policy="zero-trust-strict")
for v in violations.prioritised():
    print(f"[{v.risk_score}] {v.source} → {v.target}: {v.description}")
```

## Results

- Deployed in 3 enterprise environments
- Identified 47 previously unknown trust violations in first scan
- Reduced audit time from 3 weeks to 4 hours per network segment

## Installation

```bash
git clone https://github.com/yourusername/zt-scanner
cd zt-scanner
pip install -r requirements.txt
python scanner.py --target 10.0.0.0/8 --policy policies/zero-trust.yaml
```
