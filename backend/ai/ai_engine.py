"""
VibeGuard - AI Contextual Reasoning Engine
Uses Google Gemini API for grounded AI analysis of deterministic findings.
Falls back to mock analysis when no API key is available.
"""

import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.schemas import Finding, AIAnalysis, AttackChain, AttackChainStep, SeverityLevel
from typing import List, Dict


class AIReasoningEngine:
    """AI-augmented contextual analysis using Google Gemini."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"[VibeGuard AI] Failed to initialize Gemini: {e}")

    def analyze(self, findings: List[Finding], tf_content: str) -> AIAnalysis:
        """Perform AI contextual analysis on verified deterministic findings."""
        findings_data = [f.model_dump() for f in findings]

        if self.model and self.api_key:
            return self._gemini_analyze(findings_data, tf_content)
        else:
            return self._mock_analyze(findings_data)

    def _gemini_analyze(self, findings_data: List[Dict], tf_content: str) -> AIAnalysis:
        prompt = f"""You are an expert Cloud Security Architect performing a contextual risk analysis.

I have identified the following deterministic security findings in a Terraform configuration:

{json.dumps(findings_data, indent=2, default=str)}

The full Terraform configuration is:
---
{tf_content[:4000]}
---

Provide your analysis in the following JSON format (respond ONLY with valid JSON):
{{
  "executive_summary": "A 2-3 sentence boardroom-ready summary of the security posture",
  "technical_analysis": "Detailed technical explanation of the risks found",
  "business_impact": "Business consequences including compliance, financial, and reputational risks",
  "remediation_plan": "Prioritized remediation steps with specific Terraform fixes"
}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            return AIAnalysis(
                executive_summary=data.get("executive_summary", ""),
                technical_analysis=data.get("technical_analysis", ""),
                business_impact=data.get("business_impact", ""),
                remediation_plan=data.get("remediation_plan", ""),
            )
        except Exception as e:
            print(f"[VibeGuard AI] Gemini analysis error: {e}")
            return self._mock_analyze(findings_data)

    def _mock_analyze(self, findings_data: List[Dict]) -> AIAnalysis:
        """Generate realistic mock analysis when Gemini is unavailable."""
        count = len(findings_data)
        severities = [f.get('severity', 'Medium') for f in findings_data]
        critical_count = sum(1 for s in severities if s == 'Critical')
        high_count = sum(1 for s in severities if s == 'High')

        executive_summary = (
            f"The infrastructure audit identified {count} security findings, "
            f"including {critical_count} critical and {high_count} high-severity issues. "
            f"The configuration exhibits significant exposure to external attack vectors "
            f"through open network ports and overly permissive IAM policies. "
            f"Immediate remediation is recommended to prevent potential data breach and compliance violations."
        )

        technical_analysis = (
            "The Terraform configuration reveals multiple critical security gaps:\n\n"
            "1. **Network Perimeter Failures**: Security groups allow unrestricted inbound traffic (0.0.0.0/0) "
            "on sensitive management ports, creating direct attack vectors for brute-force and exploitation.\n\n"
            "2. **Identity & Access Management Risks**: Wildcard IAM permissions (Action: *) violate the "
            "principle of least privilege and enable full lateral movement across all AWS services.\n\n"
            "3. **Data Protection Gaps**: Public S3 bucket ACLs and unencrypted storage create pathways "
            "for data exfiltration and expose sensitive information to unauthorized access.\n\n"
            "4. **Credential Management**: Hardcoded database credentials in Terraform state files can be "
            "extracted by anyone with access to the state backend."
        )

        business_impact = (
            "**Financial Risk**: Potential data breach costs averaging $4.45M (IBM 2023 report). "
            "Unauthorized resource provisioning could generate unexpected AWS charges.\n\n"
            "**Compliance Impact**: Violations of CIS AWS Foundations Benchmark, NIST 800-53, and SOC2 "
            "controls. May result in failed audits and loss of compliance certifications.\n\n"
            "**Reputational Damage**: Public S3 bucket exposure has led to high-profile breaches. "
            "Customer trust erosion and potential legal action.\n\n"
            "**Operational Risk**: Infrastructure takeover through SSH + IAM chain could result in "
            "complete service disruption and ransomware scenarios."
        )

        remediation_plan = (
            "**Priority 1 (Immediate)**:\n"
            "- Restrict all security group SSH access to VPN/office CIDR blocks\n"
            "- Replace wildcard IAM policies with least-privilege permissions\n"
            "- Set all S3 bucket ACLs to private and enable Block Public Access\n\n"
            "**Priority 2 (Within 48 hours)**:\n"
            "- Enable encryption at rest for all RDS instances and EBS volumes\n"
            "- Migrate hardcoded credentials to AWS Secrets Manager\n"
            "- Strengthen IAM password policy (14+ chars, complexity requirements)\n\n"
            "**Priority 3 (Within 1 week)**:\n"
            "- Implement AWS Config rules for continuous compliance monitoring\n"
            "- Enable CloudTrail logging and GuardDuty threat detection\n"
            "- Conduct a full IAM access review and remove unused permissions"
        )

        return AIAnalysis(
            executive_summary=executive_summary,
            technical_analysis=technical_analysis,
            business_impact=business_impact,
            remediation_plan=remediation_plan,
        )
