from pydantic import BaseModel
from typing import List, Optional, Dict

class Finding(BaseModel):
    id: str
    rule_id: str
    resource_type: str
    resource_name: str
    severity: str  # Low, Medium, High, Critical
    title: str
    description: str
    remediation: str
    compliance_mapping: Dict[str, str]  # e.g., {"CIS": "4.1", "NIST": "AC-3"}

class AttackChain(BaseModel):
    steps: List[str]
    description: str
    risk_level: str

class AuditResult(BaseModel):
    findings: List[Finding]
    ai_analysis: Optional[str] = None
    attack_chains: List[AttackChain] = []
    posture_score: float
    summary: Dict[str, int]  # Count by severity
