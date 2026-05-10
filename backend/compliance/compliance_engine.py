"""
VibeGuard - Compliance Mapping Engine
Maps findings to CIS, NIST, and SOC2 compliance frameworks.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.schemas import Finding, ComplianceStatus
from typing import List, Dict


# Total controls per framework (simplified for MVP)
FRAMEWORK_CONTROLS = {
    "CIS": {
        "total": 12,
        "controls": ["1.8", "1.22", "2.1.1", "2.2.1", "2.3.1", "2.4", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3"]
    },
    "NIST": {
        "total": 10,
        "controls": ["AC-3", "AC-6", "SC-7", "SC-28", "IA-5", "AU-2", "CM-6", "SI-4", "CA-7", "RA-5"]
    },
    "SOC2": {
        "total": 8,
        "controls": ["CC6.1", "CC6.3", "CC6.6", "CC7.1", "CC7.2", "CC8.1", "A1.1", "A1.2"]
    },
}


class ComplianceEngine:
    """Maps findings to compliance frameworks and calculates compliance status."""

    def evaluate(self, findings: List[Finding]) -> List[ComplianceStatus]:
        # Collect all failed controls per framework
        failed_controls: Dict[str, set] = {"CIS": set(), "NIST": set(), "SOC2": set()}

        for finding in findings:
            for mapping in finding.compliance_mappings:
                fw = mapping.framework
                if fw in failed_controls:
                    failed_controls[fw].add(mapping.control_id)

        statuses = []
        for fw, info in FRAMEWORK_CONTROLS.items():
            total = info["total"]
            failed = len(failed_controls[fw])
            passed = total - failed
            pct = round((passed / total) * 100, 1) if total > 0 else 100.0
            statuses.append(ComplianceStatus(
                framework=fw,
                total_controls=total,
                passed=passed,
                failed=failed,
                percentage=pct
            ))

        return statuses
