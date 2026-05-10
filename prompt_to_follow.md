# AI-Powered Enterprise Security Guardrail Auditor
## Enterprise-Grade AI-Native Infrastructure Security Governance Platform

---

# PROJECT GOAL

Build a modern enterprise-grade AI-powered Infrastructure-as-Code (IaC) security auditing platform focused on Terraform configuration analysis.

The platform should:
- upload Terraform `.tf` files
- perform deterministic security scanning
- perform AI-assisted contextual security reasoning
- correlate risks into attack chains
- calculate posture scores
- generate explainable findings
- generate remediation suggestions
- provide compliance visibility
- display an elegant enterprise dashboard

The platform should feel like:
- a startup-ready SaaS cybersecurity platform
- enterprise-grade governance software
- an AI-native cloud security posture manager

This project is intended for:
- enterprise governance workflows
- cloud security auditing
- compliance visibility
- AI-assisted infrastructure analysis

---

# IMPORTANT ENGINEERING PHILOSOPHY

The system MUST use:
1. Deterministic detection
2. AI-assisted contextual reasoning

The AI should NEVER blindly scan raw Terraform files directly as the primary detection mechanism.

Instead:
- deterministic findings should first be generated
- structured evidence should then be passed into the LLM
- the LLM should perform contextual analysis on top of verified findings

This architecture reduces hallucinations and improves trustworthiness.

---

# HIGH-LEVEL ARCHITECTURE

Terraform File
↓
Terraform Parser Engine
↓
Deterministic Rule Engine
↓
Verified Security Findings
↓
AI Contextual Reasoning Engine
↓
Risk Correlation Engine
↓
Severity + Confidence Scoring
↓
Compliance Mapping
↓
Reporting Layer
↓
Frontend Dashboard

---

# KEY ARCHITECTURAL PRINCIPLES

## 1. Deterministic Security Validation
Known critical risks MUST always be detected deterministically.

Examples:
- public SSH exposure
- wildcard IAM permissions
- public S3 buckets
- unrestricted inbound access
- missing encryption

These findings should NEVER depend solely on AI.

---

## 2. AI-Augmented Contextual Reasoning
The LLM layer should:
- validate contextual risks
- reason about attack chains
- correlate findings
- explain business impact
- generate remediation suggestions
- generate executive summaries

The AI layer should act as:
- augmentation
NOT:
- primary truth engine

---

## 3. Explainability First
Every finding must contain:
- rule triggered
- evidence
- severity
- confidence score
- business impact
- remediation guidance
- compliance mapping

---

## 4. Modular Enterprise Architecture
The architecture MUST be cleanly separated into:
- parsing layer
- deterministic analysis layer
- AI reasoning layer
- scoring layer
- compliance layer
- reporting layer

The codebase should feel:
- scalable
- maintainable
- production-grade
- enterprise modular

---

# TECH STACK

## Frontend
- Next.js 14
- TypeScript
- TailwindCSS
- shadcn/ui
- Framer Motion
- Recharts

## Backend
- Python
- FastAPI

## AI
- Google gemini api

---

# FRONTEND DESIGN REQUIREMENTS

## Design Theme
Modern enterprise SaaS dashboard.

The UI should feel:
- premium
- clean
- modern
- intelligent
- governance-oriented

Avoid:
- hacker aesthetics
- neon cyberpunk styling
- terminal-heavy design

---

# COLOR PALETTE

Primary:
- Beige
- Lavender
- Soft Purple
- Off-white
- Deep muted purple accents

Secondary:
- soft grays
- warm neutral backgrounds

---

# TYPOGRAPHY

Use:
- Sans Serif fonts
- clean spacing
- modern enterprise typography
- elegant readability

---

# UI STYLE

Use:
- rounded cards
- glassmorphism where appropriate
- soft shadows
- hover transitions
- smooth animations
- animated counters
- polished dashboard aesthetics

The UI should resemble:
- modern AI SaaS products
- enterprise compliance dashboards
- cloud governance tools

---

# FRONTEND PAGES

## 1. Landing Dashboard

Must contain:
- Terraform upload section
- Security posture score
- Critical findings count
- High findings count
- Compliance overview
- Severity distribution chart
- Animated risk counters

---

## 2. Findings Explorer

Must display:
- finding title
- severity
- confidence score
- attack surface score
- compliance mappings
- affected resource
- deterministic evidence
- AI explanation
- remediation suggestion

Each finding should be expandable.

---

## 3. Risk Correlation Graph (HIGH PRIORITY FEATURE)

Visualize attack chains and correlated findings.

Example:

Public SSH Exposure
↓
Potential Unauthorized Access
↓
Wildcard IAM Permissions
↓
Privilege Escalation
↓
Critical Infrastructure Compromise

This should visually demonstrate:
- intelligent reasoning
- attack progression
- contextual risk relationships

This feature is extremely important for demo impact.

---

## 4. Compliance Dashboard

Display:
- CIS Benchmark mappings
- NIST mappings
- SOC2 mappings

Lightweight simulated compliance mapping is acceptable.

---

## 5. Security Posture Timeline

Show:
- posture before remediation
- posture after remediation

Example:
Before: 42/100
After: 86/100

Use animations.

---

# BACKEND ARCHITECTURE

The backend MUST be modular.

---

# REQUIRED BACKEND MODULES

## 1. Terraform Parser Engine

Responsibilities:
- parse uploaded Terraform files
- extract resources
- identify network configurations
- identify IAM policies
- identify security-related configurations

Location:
backend/parser/

---

## 2. Deterministic Rule Engine

Responsibilities:
- perform reliable rule-based detections
- detect known infrastructure risks

Location:
backend/rules/

Required detections:
- public SSH exposure
- public S3 buckets
- wildcard IAM permissions
- unrestricted ingress
- missing encryption
- weak password policy
- excessive network exposure

Rules should be configurable and modular.

---

## 3. AI Contextual Reasoning Engine

Responsibilities:
- receive deterministic findings
- reason about correlated risks
- validate suspicious configurations
- identify attack chains
- generate business impact analysis
- generate remediation guidance
- generate executive summaries

IMPORTANT:
The LLM must NEVER operate blindly.

The LLM should receive:
- deterministic findings
- severity
- evidence
- metadata
- affected resources

Example structured context:

{
  "finding": "Public SSH Exposure",
  "severity": "HIGH",
  "resource": "aws_security_group.web_sg",
  "evidence": "0.0.0.0/0 on port 22"
}

The AI should:
- reason on top of deterministic findings
- provide contextual intelligence
- identify correlated risks
- explain attack implications

Location:
backend/ai/

---

# VERY IMPORTANT AI ARCHITECTURE REQUIREMENT

The deterministic findings MUST be injected into the AI prompts as grounding context.

Example flow:

Terraform File
↓
Deterministic Detection
↓
Verified Findings
↓
Structured Findings injected into LLM prompt
↓
LLM performs contextual analysis

This grounding architecture is critical.

The AI layer should:
- extend deterministic findings
NOT:
- replace them

---

## 4. Risk Correlation Engine

Responsibilities:
- correlate multiple findings
- identify attack chains
- elevate severity when findings combine dangerously

Example:

Public SSH
+
Wildcard IAM
=
Privilege Escalation Risk

This engine should make the system feel intelligent and enterprise-grade.

Location:
backend/correlation/

---

## 5. Severity Scoring Engine

Responsibilities:
- assign severity
- calculate confidence score
- calculate attack surface score
- prioritize remediation order
- aggregate posture score

Location:
backend/scoring/

---

# REQUIRED SCORING TYPES

## Severity Score
Example:
- Critical = 40
- High = 25
- Medium = 10
- Low = 5

---

## Confidence Score
Represents certainty of finding.

Example:
- deterministic findings → 99%
- AI contextual suspicion → 72%

---

## Attack Surface Score
Represents exposure level.

Example:
- Public SSH → Very High
- Weak password policy → Medium

---

## Overall Security Posture

Example:
0–20 → Safe
21–50 → Moderate Risk
51–80 → High Risk
81+ → Critical Risk

---

## 6. Compliance Mapping Engine

Responsibilities:
- map findings to compliance frameworks

Supported:
- CIS Benchmarks
- NIST
- SOC2

Example internal mapping:

Public SSH → CIS AWS 4.1
Public S3 Bucket → NIST AC-3
Wildcard IAM → SOC2 CC6

Lightweight hardcoded mapping is acceptable.

Location:
backend/compliance/

---

## 7. Reporting Layer

Responsibilities:
- aggregate all findings
- generate frontend-ready JSON
- generate executive summaries
- generate remediation summaries

Location:
backend/reporting/

---

# REQUIRED DETECTIONS

## Critical
- Public S3 Bucket
- Public Admin Access
- Wildcard IAM Permissions

## High
- SSH exposed to 0.0.0.0/0
- Open unrestricted ingress
- Missing encryption

## Medium
- Weak password policy
- Excessive exposure

---

# AI OUTPUT REQUIREMENTS

For every finding generate:

## 1. Technical Explanation
Explain:
- what the issue is
- why dangerous
- infrastructure impact

---

## 2. Business Impact Explanation
Explain:
- business consequences
- governance impact
- compliance implications

---

## 3. Remediation Guidance
Provide:
- suggested Terraform fix
- secure alternative configuration

---

## 4. Executive Summary
Provide:
- concise enterprise risk summary
- boardroom-friendly language

---

# EXAMPLE REMEDIATION

Input:
cidr_blocks = ["0.0.0.0/0"]

Suggested Fix:
cidr_blocks = ["192.168.1.0/24"]

---

# SAMPLE DETECTION FLOW

Terraform Upload
↓
Parser Engine
↓
Deterministic Detection
↓
Structured Verified Findings
↓
AI Contextual Reasoning
↓
Attack Chain Correlation
↓
Severity + Confidence Scoring
↓
Compliance Mapping
↓
Dashboard Rendering

---

# REQUIRED FILE/FOLDER STRUCTURE

project-root/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── charts/
│   ├── dashboard/
│   ├── findings/
│   ├── compliance/
│   ├── timeline/
│   ├── correlation/
│   ├── styles/
│   ├── lib/
│   └── utils/
│
├── backend/
│   ├── main.py
│   │
│   ├── parser/
│   ├── rules/
│   ├── ai/
│   ├── correlation/
│   ├── scoring/
│   ├── compliance/
│   ├── reporting/
│   ├── models/
│   ├── utils/
│   └── sample_tf/
│
├── prompts/
│   ├── risk_analysis_prompt.txt
│   ├── remediation_prompt.txt
│   ├── executive_summary_prompt.txt
│   └── attack_chain_prompt.txt
│
├── docs/
│
├── README.md
│
└── docker-compose.yml

---

# REQUIRED SAMPLE TERRAFORM FILES

Create realistic vulnerable Terraform samples:

## 1. public_ssh.tf
Detect:
- public SSH exposure

---

## 2. public_s3.tf
Detect:
- public S3 bucket

---

## 3. wildcard_iam.tf
Detect:
- admin wildcard permissions

---

## 4. weak_password.tf
Detect:
- weak password policy

---

## 5. critical_combo.tf
Contains:
- public SSH
- public S3
- wildcard IAM

Used for:
- attack chain demo
- correlated risk analysis

---

# REQUIRED DASHBOARD METRICS

Display:
- Security Posture Score
- Critical Findings
- High Findings
- Compliance Violations
- Confidence Distribution
- Severity Distribution
- Attack Surface Overview

---

# REQUIRED VISUALIZATIONS

Use:
- animated charts
- risk graphs
- posture trends
- attack chain diagrams
- remediation priority queues

---

# REQUIRED ENGINEERING QUALITIES

The generated codebase should:
- feel enterprise modular
- use separation of concerns
- be scalable
- use reusable components
- follow clean architecture principles
- avoid monolithic design

---

# IMPORTANT POSITIONING

The platform should feel like:
- AI-assisted cloud governance software
- enterprise security posture management platform
- intelligent compliance auditing engine

NOT:
- a simple regex scanner
- a beginner Terraform parser
- a toy cybersecurity dashboard

---

# FINAL EXPECTED OUTPUT

A polished AI-native enterprise security governance platform capable of:
- uploading Terraform files
- deterministic security scanning
- AI-assisted contextual reasoning
- attack chain visualization
- posture scoring
- compliance visibility
- remediation generation
- executive reporting
- enterprise dashboard visualization

The final product should look like:
- a startup-ready SaaS cybersecurity platform
- enterprise governance software
- an AI-powered cloud security intelligence product