"""
VibeGuard - Pydantic Data Models
Enterprise-grade schemas for security findings, scoring, and audit results.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class ComplianceMapping(BaseModel):
    framework: str          # CIS, NIST, SOC2
    control_id: str         # e.g., "4.1", "AC-3", "CC6"
    description: str = ""


class Finding(BaseModel):
    id: str
    rule_id: str
    resource_type: str
    resource_name: str
    severity: SeverityLevel
    confidence: float = Field(ge=0, le=100, default=99.0)
    title: str
    description: str
    evidence: str = ""
    remediation: str = ""
    remediation_code: str = ""
    compliance_mappings: List[ComplianceMapping] = []
    attack_surface_score: float = Field(ge=0, le=100, default=50.0)
    is_ai_augmented: bool = False


class AttackChainStep(BaseModel):
    finding_id: str
    title: str
    severity: SeverityLevel


class AttackChain(BaseModel):
    id: str
    name: str
    steps: List[AttackChainStep]
    description: str
    risk_level: SeverityLevel
    business_impact: str = ""


class AIAnalysis(BaseModel):
    executive_summary: str = ""
    technical_analysis: str = ""
    business_impact: str = ""
    remediation_plan: str = ""
    contextual_findings: List[Dict] = []
    attack_chains: List[AttackChain] = []


class PostureScore(BaseModel):
    overall: float = Field(ge=0, le=100, default=100.0)
    severity_breakdown: Dict[str, int] = {}
    risk_category: str = "Safe"             # Safe, Moderate, High, Critical
    total_findings: int = 0


class ComplianceStatus(BaseModel):
    framework: str
    total_controls: int
    passed: int
    failed: int
    percentage: float


class AuditResult(BaseModel):
    filename: str
    findings: List[Finding] = []
    attack_chains: List[AttackChain] = []
    ai_analysis: Optional[AIAnalysis] = None
    posture: PostureScore = PostureScore()
    compliance: List[ComplianceStatus] = []
    raw_tf_content: str = ""
