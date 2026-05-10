from typing import List, Dict
from ..models.schemas import Finding

class RuleEngine:
    def __init__(self):
        self.rules = [
            self.check_public_s3,
            self.check_open_ssh,
            self.check_wildcard_iam,
            self.check_unrestricted_ingress,
            self.check_missing_encryption,
            self.check_weak_passwords
        ]

    def run(self, resources: List[Dict]) -> List[Finding]:
        all_findings = []
        for resource in resources:
            for rule in self.rules:
                finding = rule(resource)
                if finding:
                    all_findings.append(finding)
        return all_findings

    def check_public_s3(self, res: Dict) -> Finding:
        if res['type'] == 'aws_s3_bucket':
            acl = res['config'].get('acl', ['private'])[0]
            if acl in ['public-read', 'public-read-write']:
                return Finding(
                    id=f"S3-PUB-{res['name']}",
                    rule_id="S3-001",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity="High",
                    title="Public S3 Bucket Detected",
                    description=f"Bucket '{res['name']}' has public ACL '{acl}'.",
                    remediation="Set ACL to 'private'.",
                    compliance_mapping={"CIS": "2.1.1", "NIST": "AC-3"}
                )
        return None

    def check_open_ssh(self, res: Dict) -> Finding:
        if res['type'] == 'aws_security_group':
            ingress = res['config'].get('ingress', [])
            for rule in ingress:
                from_port = rule.get('from_port', [0])[0]
                to_port = rule.get('to_port', [0])[0]
                cidr_blocks = rule.get('cidr_blocks', [[]])[0]
                
                if (from_port <= 22 <= to_port) and "0.0.0.0/0" in cidr_blocks:
                    return Finding(
                        id=f"SG-SSH-{res['name']}",
                        rule_id="SG-001",
                        resource_type=res['type'],
                        resource_name=res['name'],
                        severity="Critical",
                        title="Open SSH Port (0.0.0.0/0)",
                        description="Security group allows SSH traffic from any IP address.",
                        remediation="Restrict SSH access to known IP ranges.",
                        compliance_mapping={"CIS": "4.1", "NIST": "SC-7"}
                    )
        return None

    def check_wildcard_iam(self, res: Dict) -> Finding:
        if res['type'] == 'aws_iam_policy':
            policy_json = res['config'].get('policy', [None])[0]
            if policy_json and '"Action": "*"' in str(policy_json) or '"Action": ["*"]' in str(policy_json):
                 return Finding(
                    id=f"IAM-WILD-{res['name']}",
                    rule_id="IAM-001",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity="High",
                    title="Wildcard IAM Permissions",
                    description="IAM policy grants administrative '*' permissions.",
                    remediation="Apply principle of least privilege.",
                    compliance_mapping={"CIS": "1.22", "SOC2": "CC6.3"}
                )
        return None

    def check_unrestricted_ingress(self, res: Dict) -> Finding:
        if res['type'] == 'aws_security_group':
            ingress = res['config'].get('ingress', [])
            for rule in ingress:
                cidr_blocks = rule.get('cidr_blocks', [[]])[0]
                if "0.0.0.0/0" in cidr_blocks:
                    return Finding(
                        id=f"SG-ING-{res['name']}",
                        rule_id="SG-002",
                        resource_type=res['type'],
                        resource_name=res['name'],
                        severity="Medium",
                        title="Unrestricted Ingress Traffic",
                        description="Security group allows traffic from any IP address.",
                        remediation="Restrict ingress to specific CIDR blocks.",
                        compliance_mapping={"NIST": "SC-7"}
                    )
        return None

    def check_missing_encryption(self, res: Dict) -> Finding:
        if res['type'] == 'aws_ebs_volume':
            encrypted = res['config'].get('encrypted', [False])[0]
            if not encrypted:
                return Finding(
                    id=f"EBS-ENC-{res['name']}",
                    rule_id="EBS-001",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity="Medium",
                    title="EBS Volume Not Encrypted",
                    description="EBS volume is not configured with server-side encryption.",
                    remediation="Set 'encrypted = true' in the resource block.",
                    compliance_mapping={"CIS": "2.2.1", "NIST": "CP-9"}
                )
        elif res['type'] == 'aws_s3_bucket':
            # Check for server_side_encryption_configuration (simplified check)
            # In a real scenario, we'd check for a separate resource or nested block
            pass
        return None

    def check_weak_passwords(self, res: Dict) -> Finding:
        if res['type'] == 'aws_iam_account_password_policy':
            min_length = res['config'].get('minimum_password_length', [8])[0]
            if min_length < 14:
                return Finding(
                    id=f"IAM-PWD-{res['name']}",
                    rule_id="IAM-002",
                    resource_type=res['type'],
                    resource_name=res['name'],
                    severity="Low",
                    title="Weak IAM Password Policy",
                    description=f"Minimum password length is {min_length}, which is less than the recommended 14.",
                    remediation="Increase minimum_password_length to 14 or more.",
                    compliance_mapping={"CIS": "1.8", "NIST": "IA-5"}
                )
        return None
