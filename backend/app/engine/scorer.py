from typing import List, Dict
from .schemas import Finding

def calculate_posture_score(findings: List[Finding]) -> float:
    """
    Calculates a score from 0-100.
    Starts at 100 and deducts points based on finding severity.
    """
    deductions = {
        "Critical": 15,
        "High": 10,
        "Medium": 5,
        "Low": 2
    }
    
    score = 100.0
    for finding in findings:
        score -= deductions.get(finding.severity, 0)
    
    return max(0.0, score)

def get_severity_summary(findings: List[Finding]) -> Dict[str, int]:
    summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1
    return summary
