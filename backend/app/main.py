from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from .engine.parser import parse_terraform, extract_resources
from .engine.rules import RuleEngine
from .engine.ai_reasoning import AIReasoningEngine
from .models.schemas import AuditResult
import json

app = FastAPI(title="VibeGuard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

rule_engine = RuleEngine()
ai_engine = AIReasoningEngine(api_key=GEMINI_API_KEY or "MOCK")

@app.post("/api/audit", response_model=AuditResult)
async def audit_terraform(file: UploadFile = File(...)):
    # Save temporary file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read content for AI
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # 1. Parse
        data = parse_terraform(temp_path)
        if not data:
            raise HTTPException(status_code=400, detail="Invalid Terraform file.")
        
        resources = extract_resources(data)
        
        # 2. Deterministic Scan
        findings = rule_engine.run(resources)
        
        # 3. AI Analysis (if API key available)
        ai_data = {}
        if ai_engine:
            findings_dicts = [f.dict() for f in findings]
            ai_data = ai_engine.analyze(findings_dicts, content)
        
        # 4. Calculate Posture Score
        severity_weights = {"Critical": 10, "High": 5, "Medium": 2, "Low": 1}
        total_score = 100
        summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        for f in findings:
            summary[f.severity] += 1
            total_score -= severity_weights.get(f.severity, 0)
        
        total_score = max(0, total_score)
        
        # 5. Save output
        output_file = f"Output/audit_{file.filename}_{len(os.listdir('Output'))}.json"
        result = {
            "findings": findings,
            "ai_analysis": ai_data.get("ai_analysis"),
            "attack_chains": ai_data.get("attack_chains", []),
            "posture_score": total_score,
            "summary": summary
        }
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4, default=lambda o: o.dict() if hasattr(o, 'dict') else o)
        
        return result

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/dashboard")
async def get_dashboard():
    # Return aggregated data from past audits or a summary
    # For now, just a placeholder
    return {"message": "Dashboard data endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
