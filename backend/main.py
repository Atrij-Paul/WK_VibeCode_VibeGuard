"""
VibeGuard - FastAPI Main Application
Enterprise-grade AI-powered Infrastructure Security Auditor.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import sys
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Module imports
sys.path.insert(0, os.path.dirname(__file__))
from parser.tf_parser import TerraformParser
from rules.rule_engine import RuleEngine
from ai.ai_engine import AIReasoningEngine
from correlation.correlation_engine import CorrelationEngine
from scoring.scoring_engine import ScoringEngine
from compliance.compliance_engine import ComplianceEngine
from models.schemas import AuditResult

app = FastAPI(
    title="VibeGuard API",
    description="AI-Powered Enterprise Security Guardrail Auditor",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
tf_parser = TerraformParser()
rule_engine = RuleEngine()
ai_engine = AIReasoningEngine()
correlation_engine = CorrelationEngine()
scoring_engine = ScoringEngine()
compliance_engine = ComplianceEngine()

# In-memory audit history for dashboard
audit_history = []


@app.get("/")
async def root():
    return {"status": "online", "service": "VibeGuard API", "version": "1.0.0"}


@app.post("/api/audit")
async def audit_terraform(file: UploadFile = File(...)):
    """
    Main audit endpoint.
    Accepts a .tf file, runs full security analysis pipeline, returns results.
    """
    if not file.filename.endswith('.tf'):
        raise HTTPException(status_code=400, detail="Only .tf files are supported.")

    content = await file.read()
    tf_content = content.decode('utf-8')

    # ─── Pipeline ─────────────────────────────────────
    # 1. Parse Terraform
    resources = tf_parser.parse_file(tf_content)
    if not resources:
        raise HTTPException(status_code=400, detail="No resources found in the Terraform file.")

    # 2. Deterministic Rule Scan
    findings = rule_engine.scan(resources)

    # 3. Risk Correlation
    attack_chains = correlation_engine.correlate(findings)

    # 4. AI Contextual Analysis (grounded on deterministic findings)
    ai_analysis = ai_engine.analyze(findings, tf_content)

    # 5. Posture Scoring
    posture = scoring_engine.calculate(findings, attack_chains)

    # 6. Compliance Mapping
    compliance = compliance_engine.evaluate(findings)

    # Build result
    result = AuditResult(
        filename=file.filename,
        findings=findings,
        attack_chains=attack_chains,
        ai_analysis=ai_analysis,
        posture=posture,
        compliance=compliance,
        raw_tf_content=tf_content,
    )

    # Save to Output folder
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'Output')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"audit_{file.filename}_{timestamp}.json")
        with open(output_path, 'w') as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
    except Exception as e:
        print(f"[VibeGuard] Error saving output: {e}")

    # Store in history
    audit_history.append({
        "filename": file.filename,
        "timestamp": datetime.now().isoformat(),
        "posture": posture.model_dump(),
        "finding_count": len(findings),
        "chain_count": len(attack_chains),
    })

    return result.model_dump()


@app.get("/api/history")
async def get_audit_history():
    """Return list of past audits."""
    return audit_history


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
