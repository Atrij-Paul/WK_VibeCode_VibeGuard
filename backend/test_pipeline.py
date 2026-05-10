"""Quick test of the VibeGuard audit pipeline."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from parser.tf_parser import TerraformParser
from rules.rule_engine import RuleEngine
from correlation.correlation_engine import CorrelationEngine
from scoring.scoring_engine import ScoringEngine
from compliance.compliance_engine import ComplianceEngine

p = TerraformParser()
r = RuleEngine()
c = CorrelationEngine()
s = ScoringEngine()
comp = ComplianceEngine()

test_file = os.path.join(os.path.dirname(__file__), '..', 'Test', 'critical_combo.tf')
content = open(test_file).read()

resources = p.parse_file(content)
print(f"Resources parsed: {len(resources)}")
for res in resources:
    print(f"  {res['type']}.{res['name']}")

findings = r.scan(resources)
print(f"\nFindings: {len(findings)}")
for f in findings:
    print(f"  [{f.severity.value}] {f.title} → {f.evidence}")

chains = c.correlate(findings)
print(f"\nAttack Chains: {len(chains)}")
for ch in chains:
    print(f"  {ch.name} ({ch.risk_level.value})")

posture = s.calculate(findings, chains)
print(f"\nPosture Score: {posture.overall} ({posture.risk_category})")
print(f"Breakdown: {posture.severity_breakdown}")

compliance_status = comp.evaluate(findings)
print(f"\nCompliance:")
for cs in compliance_status:
    print(f"  {cs.framework}: {cs.passed}/{cs.total_controls} passed ({cs.percentage}%)")
