import google.generativeai as genai
import os
import json
from typing import List, Dict

class AIReasoningEngine:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze(self, findings: List[Dict], tf_content: str):
        if not os.getenv("GEMINI_API_KEY"):
            return self._get_mock_analysis(findings)

        prompt = f"""
        You are an expert Cloud Security Architect. 
        I have identified the following deterministic findings in a Terraform configuration:
        {json.dumps(findings, indent=2)}

        The full Terraform configuration is provided below:
        ---
        {tf_content}
        ---

        Perform a contextual risk analysis based on these findings and the configuration.
        Provide your response in JSON format with the following keys:
        1. 'ai_analysis': A high-level executive summary of the security posture.
        2. 'attack_chains': A list of objects with 'steps' (list of strings) and 'description' (string) showing how findings could be chained.
        3. 'contextual_findings': Additional findings or deeper insights for existing findings, including technical explanation and business impact.
        4. 'remediation_plan': A structured plan with code snippets where applicable.
        
        Assign a 'risk_level' (Low, Medium, High, Critical) to each attack chain.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return self._get_mock_analysis(findings)

    def _get_mock_analysis(self, findings: List[Dict]):
        return {
            "ai_analysis": "MOCK ANALYSIS: The infrastructure exhibits high risk due to exposed management ports and permissive IAM roles. An attacker could potentially gain initial access via SSH and escalate privileges using the wildcard IAM permissions found on the EC2 instance profile.",
            "attack_chains": [
                {
                    "steps": ["Open SSH", "Wildcard IAM", "Data Exfiltration"],
                    "description": "An attacker can brute-force the open SSH port, leverage the '*' IAM permissions to list S3 buckets, and exfiltrate sensitive data from the public buckets.",
                    "risk_level": "Critical"
                }
            ],
            "contextual_findings": [
                {
                    "title": "Combined Risk: Public Access + Admin Rights",
                    "explanation": "The combination of 0.0.0.0/0 SSH access and '*' permissions is a 'toxic combination' that effectively bypasses all cloud perimeter controls.",
                    "business_impact": "High probability of data breach and regulatory non-compliance (SOC2/GDPR)."
                }
            ],
            "remediation_plan": "1. Restrict SG ingress to VPN IP. 2. Replace '*' with specific Actions (e.g., s3:GetObject). 3. Enable S3 Block Public Access."
        }
