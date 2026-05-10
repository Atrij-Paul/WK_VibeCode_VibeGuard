"""
VibeGuard - Deterministic Rule Engine
Hardcoded security rules for Terraform infrastructure analysis.
Each rule returns a Finding or None.
"""

import re
from typing import List, Dict, Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.schemas import Finding, SeverityLevel, ComplianceMapping


class RuleEngine:
    """Deterministic rule-based security scanner."""

    def scan(self, resources: List[Dict]) -> List[Finding]:
        """Run all rules against all parsed resources."""
        findings = []
        for res in resources:
            for rule in self._get_rules():
                result = rule(res)
                if result:
                    findings.append(result)
        return findings

    def _get_rules(self):
        return [
            self._check_public_ssh,
            self._check_open_ingress,
            self._check_public_s3,
            self._check_wildcard_iam,
            self._check_missing_encryption,
            self._check_weak_password,
            self._check_hardcoded_credentials,
        ]

    # ── Rule 1: Public SSH ──────────────────────────────────
    def _check_public_ssh(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_security_group':
            return None
        for ingress in res['config'].get('ingress', []):
            if not isinstance(ingress, dict):
                continue
            from_port = ingress.get('from_port', 0)
            to_port = ingress.get('to_port', 0)
            cidrs = ingress.get('cidr_blocks', [])
            if isinstance(from_port, str):
                try: from_port = int(from_port)
                except: from_port = 0
            if isinstance(to_port, str):
                try: to_port = int(to_port)
                except: to_port = 0
            if isinstance(cidrs, str):
                cidrs = [cidrs]
            if from_port <= 22 <= to_port and "0.0.0.0/0" in cidrs:
                return Finding(
                    id=f"SSH-{res['name']}",
                    rule_id="SG-001",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity=SeverityLevel.CRITICAL,
                    confidence=99.0,
                    title="Public SSH Exposure (0.0.0.0/0)",
                    description=f"Security group '{res['name']}' allows SSH (port 22) from any IP address globally. This exposes the instance to brute-force attacks and unauthorized access.",
                    evidence=f"ingress rule: from_port=22, to_port=22, cidr_blocks=[\"0.0.0.0/0\"]",
                    remediation="Restrict SSH access to known IP ranges (e.g., your VPN or office CIDR).",
                    remediation_code='cidr_blocks = ["10.0.0.0/8"]  # Replace with your VPN CIDR',
                    compliance_mappings=[
                        ComplianceMapping(framework="CIS", control_id="4.1", description="Ensure no security groups allow ingress from 0.0.0.0/0 to port 22"),
                        ComplianceMapping(framework="NIST", control_id="SC-7", description="Boundary Protection"),
                        ComplianceMapping(framework="SOC2", control_id="CC6.1", description="Logical and Physical Access Controls"),
                    ],
                    attack_surface_score=95.0,
                )
        return None

    # ── Rule 2: Unrestricted Ingress ────────────────────────
    def _check_open_ingress(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_security_group':
            return None
        for ingress in res['config'].get('ingress', []):
            if not isinstance(ingress, dict):
                continue
            from_port = ingress.get('from_port', 0)
            to_port = ingress.get('to_port', 0)
            cidrs = ingress.get('cidr_blocks', [])
            if isinstance(from_port, str):
                try: from_port = int(from_port)
                except: from_port = 0
            if isinstance(to_port, str):
                try: to_port = int(to_port)
                except: to_port = 0
            if isinstance(cidrs, str):
                cidrs = [cidrs]
            # Only flag if it's a wide port range (not just SSH which is caught by rule 1)
            port_range = to_port - from_port
            if port_range > 100 and "0.0.0.0/0" in cidrs:
                return Finding(
                    id=f"ING-{res['name']}",
                    rule_id="SG-002",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity=SeverityLevel.HIGH,
                    confidence=99.0,
                    title="Unrestricted Ingress — Wide Port Range Open",
                    description=f"Security group '{res['name']}' allows traffic on ports {from_port}-{to_port} from 0.0.0.0/0. This exposes multiple services to the internet.",
                    evidence=f"ingress rule: from_port={from_port}, to_port={to_port}, cidr_blocks=[\"0.0.0.0/0\"]",
                    remediation="Restrict ingress to specific ports and known CIDR blocks.",
                    remediation_code='from_port = 443\nto_port   = 443\ncidr_blocks = ["10.0.0.0/8"]',
                    compliance_mappings=[
                        ComplianceMapping(framework="NIST", control_id="SC-7", description="Boundary Protection"),
                        ComplianceMapping(framework="CIS", control_id="4.2", description="Ensure no SG allows unrestricted ingress"),
                    ],
                    attack_surface_score=85.0,
                )
        return None

    # ── Rule 3: Public S3 Bucket ────────────────────────────
    def _check_public_s3(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_s3_bucket_acl':
            return None
        acl = res['config'].get('acl', 'private')
        if isinstance(acl, list):
            acl = acl[0] if acl else 'private'
        if acl in ('public-read', 'public-read-write'):
            bucket_ref = res['config'].get('bucket', res['name'])
            return Finding(
                id=f"S3-{res['name']}",
                rule_id="S3-001",
                resource_type=res['type'],
                resource_name=res['name'],
                severity=SeverityLevel.CRITICAL,
                confidence=99.0,
                title="Public S3 Bucket Detected",
                description=f"S3 bucket ACL resource '{res['name']}' is set to '{acl}', making bucket contents publicly accessible. This can lead to data exposure.",
                evidence=f"acl = \"{acl}\"",
                remediation="Set the bucket ACL to 'private' and enable S3 Block Public Access.",
                remediation_code='acl = "private"\n\n# Also add:\nresource "aws_s3_bucket_public_access_block" "block" {\n  bucket = aws_s3_bucket.example.id\n  block_public_acls = true\n  block_public_policy = true\n}',
                compliance_mappings=[
                    ComplianceMapping(framework="CIS", control_id="2.1.1", description="Ensure S3 Bucket Policy does not allow public access"),
                    ComplianceMapping(framework="NIST", control_id="AC-3", description="Access Enforcement"),
                    ComplianceMapping(framework="SOC2", control_id="CC6.1", description="Logical and Physical Access Controls"),
                ],
                attack_surface_score=90.0,
            )
        return None

    # ── Rule 4: Wildcard IAM Permissions ────────────────────
    def _check_wildcard_iam(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_iam_policy':
            return None
        policy_raw = res['config'].get('_policy_raw', '')
        raw_block = res.get('raw', '')
        combined = policy_raw + raw_block
        # Check for Action = "*"
        if re.search(r'Action\s*=\s*"\*"', combined) or '"Action": "*"' in combined or '"Action":"*"' in combined:
            return Finding(
                id=f"IAM-{res['name']}",
                rule_id="IAM-001",
                resource_type=res['type'],
                resource_name=res['name'],
                severity=SeverityLevel.CRITICAL,
                confidence=99.0,
                title="Wildcard IAM Permissions (Action: *)",
                description=f"IAM policy '{res['name']}' grants full administrative '*' permissions on all resources. This violates the principle of least privilege.",
                evidence='Action = "*", Resource = "*"',
                remediation="Replace wildcard permissions with specific, least-privilege actions.",
                remediation_code='Action = [\n  "s3:GetObject",\n  "s3:ListBucket"\n]\nResource = "arn:aws:s3:::my-bucket/*"',
                compliance_mappings=[
                    ComplianceMapping(framework="CIS", control_id="1.22", description="Ensure IAM policies are attached only to groups or roles"),
                    ComplianceMapping(framework="NIST", control_id="AC-6", description="Least Privilege"),
                    ComplianceMapping(framework="SOC2", control_id="CC6.3", description="Role-Based Access Controls"),
                ],
                attack_surface_score=92.0,
            )
        return None

    # ── Rule 5: Missing Encryption ──────────────────────────
    def _check_missing_encryption(self, res: Dict) -> Optional[Finding]:
        if res['type'] == 'aws_db_instance':
            encrypted = res['config'].get('storage_encrypted', False)
            if encrypted is False or encrypted == 'false':
                return Finding(
                    id=f"ENC-{res['name']}",
                    rule_id="ENC-001",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity=SeverityLevel.HIGH,
                    confidence=99.0,
                    title="Database Storage Not Encrypted",
                    description=f"RDS instance '{res['name']}' has storage_encrypted set to false. Data at rest is unprotected.",
                    evidence="storage_encrypted = false",
                    remediation="Enable encryption at rest for the database instance.",
                    remediation_code='storage_encrypted = true',
                    compliance_mappings=[
                        ComplianceMapping(framework="CIS", control_id="2.3.1", description="Ensure RDS encryption is enabled"),
                        ComplianceMapping(framework="NIST", control_id="SC-28", description="Protection of Information at Rest"),
                    ],
                    attack_surface_score=70.0,
                )
        if res['type'] == 'aws_ebs_volume':
            encrypted = res['config'].get('encrypted', False)
            if encrypted is False or encrypted == 'false':
                return Finding(
                    id=f"ENC-{res['name']}",
                    rule_id="ENC-002",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity=SeverityLevel.HIGH,
                    confidence=99.0,
                    title="EBS Volume Not Encrypted",
                    description=f"EBS volume '{res['name']}' is not encrypted. Data at rest is vulnerable.",
                    evidence="encrypted = false",
                    remediation="Set encrypted = true on the EBS volume.",
                    remediation_code='encrypted = true',
                    compliance_mappings=[
                        ComplianceMapping(framework="CIS", control_id="2.2.1", description="Ensure EBS volume encryption is enabled"),
                        ComplianceMapping(framework="NIST", control_id="SC-28", description="Protection of Information at Rest"),
                    ],
                    attack_surface_score=65.0,
                )
        return None

    # ── Rule 6: Weak Password Policy ───────────────────────
    def _check_weak_password(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_iam_account_password_policy':
            return None
        min_len = res['config'].get('minimum_password_length', 8)
        if isinstance(min_len, str):
            try: min_len = int(min_len)
            except: min_len = 8
        req_symbols = res['config'].get('require_symbols', True)
        req_numbers = res['config'].get('require_numbers', True)
        req_upper = res['config'].get('require_uppercase_characters', True)

        issues = []
        if min_len < 14:
            issues.append(f"minimum_password_length={min_len} (should be ≥14)")
        if req_symbols is False or req_symbols == 'false':
            issues.append("require_symbols=false")
        if req_numbers is False or req_numbers == 'false':
            issues.append("require_numbers=false")
        if req_upper is False or req_upper == 'false':
            issues.append("require_uppercase_characters=false")

        if issues:
            return Finding(
                id=f"PWD-{res['name']}",
                rule_id="IAM-002",
                resource_type=res['type'],
                resource_name=res['name'],
                severity=SeverityLevel.MEDIUM,
                confidence=99.0,
                title="Weak IAM Password Policy",
                description=f"IAM account password policy '{res['name']}' does not meet security best practices.",
                evidence="; ".join(issues),
                remediation="Strengthen the password policy: minimum 14 characters, require symbols, numbers, and uppercase.",
                remediation_code='minimum_password_length        = 14\nrequire_symbols                = true\nrequire_numbers                = true\nrequire_uppercase_characters   = true\nrequire_lowercase_characters   = true',
                compliance_mappings=[
                    ComplianceMapping(framework="CIS", control_id="1.8", description="Ensure IAM password policy requires minimum length of 14"),
                    ComplianceMapping(framework="NIST", control_id="IA-5", description="Authenticator Management"),
                ],
                attack_surface_score=45.0,
            )
        return None

    # ── Rule 7: Hardcoded Credentials ──────────────────────
    def _check_hardcoded_credentials(self, res: Dict) -> Optional[Finding]:
        if res['type'] != 'aws_db_instance':
            return None
        password = res['config'].get('password', '')
        if isinstance(password, str) and password and not password.startswith('var.') and not password.startswith('$'):
            return Finding(
                id=f"CRED-{res['name']}",
                rule_id="SEC-001",
                resource_type=res['type'],
                resource_name=res['name'],
                severity=SeverityLevel.HIGH,
                confidence=95.0,
                title="Hardcoded Database Credentials",
                description=f"Database instance '{res['name']}' has a hardcoded password in plaintext. Credentials should be managed via secrets manager.",
                evidence=f"password = \"{'*' * len(password)}\" (hardcoded)",
                remediation="Use AWS Secrets Manager or SSM Parameter Store for credentials.",
                remediation_code='password = var.db_password\n\n# Or use Secrets Manager:\n# password = data.aws_secretsmanager_secret_version.db.secret_string',
                compliance_mappings=[
                    ComplianceMapping(framework="CIS", control_id="2.4", description="Ensure credentials are not hardcoded"),
                    ComplianceMapping(framework="NIST", control_id="IA-5", description="Authenticator Management"),
                    ComplianceMapping(framework="SOC2", control_id="CC6.1", description="Logical Access Controls"),
                ],
                attack_surface_score=80.0,
            )
        return None
