"""
VibeGuard - Severity & Posture Scoring Engine
Calculates overall security posture and risk categorization.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.schemas import Finding, AttackChain, PostureScore, SeverityLevel
from typing import List


SEVERITY_WEIGHTS = {
    SeverityLevel.CRITICAL: 25,
    SeverityLevel.HIGH: 15,
    SeverityLevel.MEDIUM: 8,
    SeverityLevel.LOW: 3,
    SeverityLevel.INFO: 0,
}


class ScoringEngine:
    """Calculates security posture scores from findings and attack chains."""

    def calculate(self, findings: List[Finding], attack_chains: List[AttackChain]) -> PostureScore:
        # Count by severity
        breakdown = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        total_deduction = 0

        for f in findings:
            breakdown[f.severity.value] += 1
            total_deduction += SEVERITY_WEIGHTS.get(f.severity, 0)

        # Attack chains amplify risk
        chain_penalty = len(attack_chains) * 10
        total_deduction += chain_penalty

        # Calculate score (0-100, higher = more risk)
        risk_score = min(100, total_deduction)

        # Determine category
        if risk_score <= 20:
            category = "Safe"
        elif risk_score <= 50:
            category = "Moderate Risk"
        elif risk_score <= 80:
            category = "High Risk"
        else:
            category = "Critical Risk"

        return PostureScore(
            overall=risk_score,
            severity_breakdown=breakdown,
            risk_category=category,
            total_findings=len(findings)
        )
