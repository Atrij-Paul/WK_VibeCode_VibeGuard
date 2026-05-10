"""
VibeGuard - Risk Correlation Engine
Identifies attack chains by correlating multiple findings.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.schemas import Finding, AttackChain, AttackChainStep, SeverityLevel
from typing import List


class CorrelationEngine:
    """Correlates findings into attack chains."""

    def correlate(self, findings: List[Finding]) -> List[AttackChain]:
        chains = []
        finding_map = {f.rule_id: f for f in findings}
        finding_ids = set(finding_map.keys())

        # Chain 1: Public SSH + Wildcard IAM = Cloud Takeover
        if 'SG-001' in finding_ids and 'IAM-001' in finding_ids:
            chains.append(AttackChain(
                id="CHAIN-001",
                name="Infrastructure Takeover via SSH + Admin IAM",
                steps=[
                    AttackChainStep(
                        finding_id=finding_map['SG-001'].id,
                        title="Public SSH Exposure",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-LATERAL",
                        title="Unauthorized Server Access",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id=finding_map['IAM-001'].id,
                        title="Wildcard IAM Privilege Escalation",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-TAKEOVER",
                        title="Full Cloud Infrastructure Compromise",
                        severity=SeverityLevel.CRITICAL
                    ),
                ],
                description="An attacker can exploit open SSH to gain server access, then leverage wildcard IAM permissions to escalate privileges and take over the entire cloud infrastructure.",
                risk_level=SeverityLevel.CRITICAL,
                business_impact="Complete infrastructure compromise. Potential data exfiltration, service disruption, and regulatory penalties."
            ))

        # Chain 2: Public S3 + Wildcard IAM = Data Exfiltration
        if 'S3-001' in finding_ids and 'IAM-001' in finding_ids:
            chains.append(AttackChain(
                id="CHAIN-002",
                name="Data Exfiltration via Public S3 + Admin Permissions",
                steps=[
                    AttackChainStep(
                        finding_id=finding_map['S3-001'].id,
                        title="Public S3 Bucket Exposure",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-DISCOVERY",
                        title="Sensitive Data Discovery",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id=finding_map['IAM-001'].id,
                        title="Wildcard IAM — Access All Resources",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-EXFIL",
                        title="Mass Data Exfiltration",
                        severity=SeverityLevel.CRITICAL
                    ),
                ],
                description="Public S3 buckets expose data to the internet. Combined with wildcard IAM permissions, an attacker can access and exfiltrate all cloud resources and data.",
                risk_level=SeverityLevel.CRITICAL,
                business_impact="Data breach risk. Potential GDPR/CCPA violations, financial loss, and reputational damage."
            ))

        # Chain 3: Open Ingress + Missing Encryption = Data Interception
        if 'SG-002' in finding_ids and 'ENC-001' in finding_ids:
            chains.append(AttackChain(
                id="CHAIN-003",
                name="Data Interception via Open Network + Unencrypted Storage",
                steps=[
                    AttackChainStep(
                        finding_id=finding_map['SG-002'].id,
                        title="Unrestricted Network Ingress",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id=finding_map['ENC-001'].id,
                        title="Unencrypted Database Storage",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id="STEP-INTERCEPT",
                        title="Data Interception / Theft",
                        severity=SeverityLevel.CRITICAL
                    ),
                ],
                description="Unrestricted network access combined with unencrypted storage allows attackers to access and read sensitive data in transit and at rest.",
                risk_level=SeverityLevel.HIGH,
                business_impact="Sensitive data exposure without encryption protection. Compliance violations for data-at-rest requirements."
            ))

        # Chain 4: Public SSH + Hardcoded Creds = Database Compromise
        if 'SG-001' in finding_ids and 'SEC-001' in finding_ids:
            chains.append(AttackChain(
                id="CHAIN-004",
                name="Database Compromise via SSH + Hardcoded Credentials",
                steps=[
                    AttackChainStep(
                        finding_id=finding_map['SG-001'].id,
                        title="Public SSH Exposure",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-ACCESS",
                        title="Server Access Gained",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id=finding_map['SEC-001'].id,
                        title="Hardcoded Database Credentials Found",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id="STEP-DB-COMPROMISE",
                        title="Full Database Compromise",
                        severity=SeverityLevel.CRITICAL
                    ),
                ],
                description="Open SSH allows server access where hardcoded database credentials can be discovered in terraform config, leading to full database compromise.",
                risk_level=SeverityLevel.CRITICAL,
                business_impact="Direct database access with stolen credentials. Complete data breach and potential ransomware scenario."
            ))

        # Chain 5: Weak Password + Wildcard IAM = Account Takeover
        if 'IAM-002' in finding_ids and 'IAM-001' in finding_ids:
            chains.append(AttackChain(
                id="CHAIN-005",
                name="Account Takeover via Weak Passwords + Admin IAM",
                steps=[
                    AttackChainStep(
                        finding_id=finding_map['IAM-002'].id,
                        title="Weak Password Policy",
                        severity=SeverityLevel.MEDIUM
                    ),
                    AttackChainStep(
                        finding_id="STEP-BRUTE",
                        title="Password Brute Force / Credential Stuffing",
                        severity=SeverityLevel.HIGH
                    ),
                    AttackChainStep(
                        finding_id=finding_map['IAM-001'].id,
                        title="Wildcard IAM Permissions Exploited",
                        severity=SeverityLevel.CRITICAL
                    ),
                    AttackChainStep(
                        finding_id="STEP-ACCOUNT-TAKEOVER",
                        title="Full AWS Account Takeover",
                        severity=SeverityLevel.CRITICAL
                    ),
                ],
                description="Weak password policies allow brute-force attacks. Once an account is compromised, wildcard IAM grants full administrative control.",
                risk_level=SeverityLevel.CRITICAL,
                business_impact="Complete AWS account compromise. Unauthorized resource provisioning, data deletion, and financial abuse."
            ))

        return chains
