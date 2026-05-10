"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Shield, AlertTriangle, CheckCircle, Activity, ChevronRight, FileText, Zap } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";
import axios from "axios";

const COLORS = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#3b82f6",
  Safe: "#22c55e"
};

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post("http://localhost:8000/api/audit", formData);
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to audit file. Ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const severityData = results ? [
    { name: "Critical", value: results.summary.Critical, color: COLORS.Critical },
    { name: "High", value: results.summary.High, color: COLORS.High },
    { name: "Medium", value: results.summary.Medium, color: COLORS.Medium },
    { name: "Low", value: results.summary.Low, color: COLORS.Low },
  ].filter(d => d.value > 0) : [];

  return (
    <div className="min-h-screen bg-background text-foreground p-8 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-xl">
            <Shield className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">VibeGuard</h1>
            <p className="text-sm text-muted-foreground">AI-Powered Infrastructure Auditor</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
           <div className="text-right">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">System Status</p>
              <p className="text-sm font-semibold flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Operational
              </p>
           </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload & Summary Section */}
        <div className="lg:col-span-4 space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-border rounded-3xl p-8 shadow-sm"
          >
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary" />
              Scan Infrastructure
            </h2>
            <div className="relative group">
              <input 
                type="file" 
                onChange={handleFileUpload}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                accept=".tf"
              />
              <div className="border-2 border-dashed border-muted group-hover:border-primary/50 transition-colors rounded-2xl p-10 text-center space-y-4">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <FileText className="w-8 h-8 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">{file ? file.name : "Drop Terraform file"}</p>
                  <p className="text-xs text-muted-foreground mt-1">Supports .tf files up to 10MB</p>
                </div>
              </div>
            </div>
            {loading && (
              <div className="mt-4 flex items-center justify-center gap-2 text-primary">
                <Activity className="w-4 h-4 animate-spin" />
                <span className="text-sm font-medium">AI Analysis in progress...</span>
              </div>
            )}
            {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}
          </motion.div>

          {results && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-primary/5 border border-primary/10 rounded-3xl p-8 text-center"
            >
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-widest mb-2">Posture Score</h3>
              <div className="relative inline-flex items-center justify-center">
                <svg className="w-40 h-40 transform -rotate-90">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="transparent"
                    stroke="currentColor"
                    strokeWidth="12"
                    className="text-muted/20"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="transparent"
                    stroke="currentColor"
                    strokeWidth="12"
                    strokeDasharray={440}
                    strokeDashoffset={440 - (440 * results.posture_score) / 100}
                    className="text-primary transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-black text-primary">{results.posture_score}</span>
                  <span className="text-xs font-bold text-muted-foreground">CRITICALITY</span>
                </div>
              </div>
              <p className="mt-6 text-sm text-muted-foreground font-medium italic">
                "{results.posture_score > 80 ? "Excellent security posture. Minimal risks identified." : "Action required. Multiple high-risk patterns detected."}"
              </p>
            </motion.div>
          )}
        </div>

        {/* Findings & Analysis Section */}
        <div className="lg:col-span-8 space-y-8">
          {!results && !loading && (
            <div className="h-full flex flex-col items-center justify-center py-20 text-center space-y-6">
              <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center animate-pulse">
                <Zap className="w-10 h-10 text-muted-foreground" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">Ready for Audit</h3>
                <p className="text-muted-foreground max-w-sm mx-auto">Upload a Terraform configuration to begin deterministic scanning and contextual AI reasoning.</p>
              </div>
            </div>
          )}

          {results && (
            <div className="space-y-8">
              {/* Charts Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-card border border-border rounded-3xl p-6">
                  <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={severityData}
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {severityData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                <div className="bg-card border border-border rounded-3xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    AI Reasoning
                  </h3>
                  <div className="prose prose-sm max-h-64 overflow-y-auto text-muted-foreground">
                    <p>{results.ai_analysis || "AI analysis not available for this run."}</p>
                  </div>
                </div>
              </div>

              {/* Attack Chains */}
              {results.attack_chains.length > 0 && (
                <div className="bg-destructive/5 border border-destructive/20 rounded-3xl p-8">
                   <h3 className="text-lg font-bold text-destructive flex items-center gap-2 mb-4">
                     <AlertTriangle className="w-6 h-6" />
                     Critical Attack Chains Detected
                   </h3>
                   <div className="space-y-4">
                     {results.attack_chains.map((chain: any, idx: number) => (
                       <div key={idx} className="bg-white/50 p-4 rounded-xl border border-destructive/10">
                          <p className="font-semibold text-destructive">{chain.risk_level} Risk</p>
                          <div className="flex items-center gap-2 my-2">
                            {chain.steps.map((step: string, sIdx: number) => (
                              <React.Fragment key={sIdx}>
                                <span className="text-xs bg-destructive/10 px-2 py-1 rounded-md">{step}</span>
                                {sIdx < chain.steps.length - 1 && <ChevronRight className="w-4 h-4 text-muted-foreground" />}
                              </React.Fragment>
                            ))}
                          </div>
                          <p className="text-sm text-muted-foreground">{chain.description}</p>
                       </div>
                     ))}
                   </div>
                </div>
              )}

              {/* Findings List */}
              <div className="space-y-4">
                <h3 className="text-xl font-bold">Vulnerability Report</h3>
                {results.findings.map((finding: any, idx: number) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="group bg-card border border-border hover:border-primary/30 transition-all rounded-2xl p-6"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex gap-4">
                        <div className={`p-3 rounded-xl ${
                          finding.severity === 'Critical' ? 'bg-red-100 text-red-600' : 
                          finding.severity === 'High' ? 'bg-orange-100 text-orange-600' :
                          'bg-yellow-100 text-yellow-600'
                        }`}>
                          <AlertTriangle className="w-6 h-6" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                               finding.severity === 'Critical' ? 'bg-red-500 text-white' : 
                               finding.severity === 'High' ? 'bg-orange-500 text-white' :
                               'bg-yellow-500 text-white'
                            }`}>
                              {finding.severity}
                            </span>
                            <span className="text-xs text-muted-foreground font-mono">{finding.rule_id}</span>
                          </div>
                          <h4 className="text-lg font-bold mt-1">{finding.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{finding.description}</p>
                          <div className="flex items-center gap-4 mt-4">
                             <div className="text-xs font-medium bg-muted px-3 py-1.5 rounded-lg flex items-center gap-1">
                               <FileText className="w-3 h-3" />
                               {finding.resource_type}.{finding.resource_name}
                             </div>
                             {Object.entries(finding.compliance_mapping).map(([standard, value]) => (
                               <div key={standard} className="text-[10px] font-bold bg-primary/5 text-primary border border-primary/20 px-3 py-1.5 rounded-lg">
                                 {standard}: {value}
                               </div>
                             ))}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                         <p className="text-xs font-bold text-muted-foreground uppercase mb-2">Remediation</p>
                         <p className="text-sm font-medium text-green-600 flex items-center gap-1">
                           <CheckCircle className="w-4 h-4" />
                           {finding.remediation}
                         </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
