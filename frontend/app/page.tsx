"use client";
import React, { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Upload, AlertTriangle, CheckCircle, Activity, FileText, Zap, ChevronDown, ChevronRight, Lock, Eye, BarChart3, GitBranch, ArrowRight } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, RadialBarChart, RadialBar } from "recharts";
import { auditFile, AuditResult, Finding, AttackChain, ComplianceStatus } from "@/lib/api";
import ReactMarkdown from "react-markdown";

const SEV_COLORS: Record<string, string> = { Critical: "#dc2626", High: "#ea580c", Medium: "#d97706", Low: "#2563eb", Info: "#6b7280" };
const COMP_COLORS = ["#7c3aed", "#8b5cf6", "#a78bfa"];

function AnimatedCounter({ value, suffix = "" }: { value: number; suffix?: string }) {
  const [display, setDisplay] = React.useState(0);
  React.useEffect(() => {
    let start = 0; const end = value; const dur = 1200; const step = Math.max(1, Math.floor(end / (dur / 16)));
    const timer = setInterval(() => { start += step; if (start >= end) { setDisplay(end); clearInterval(timer); } else setDisplay(start); }, 16);
    return () => clearInterval(timer);
  }, [value]);
  return <span>{display}{suffix}</span>;
}

function PostureGauge({ score, category }: { score: number; category: string }) {
  const r = 70, circ = 2 * Math.PI * r;
  const catColor = score >= 81 ? "#dc2626" : score >= 51 ? "#ea580c" : score >= 21 ? "#d97706" : "#22c55e";
  return (
    <div className="flex flex-col items-center">
      <svg width="180" height="180" className="-rotate-90">
        <circle cx="90" cy="90" r={r} fill="transparent" stroke="currentColor" strokeWidth="14" className="text-muted/30" />
        <motion.circle cx="90" cy="90" r={r} fill="transparent" stroke={catColor} strokeWidth="14" strokeLinecap="round"
          strokeDasharray={circ} initial={{ strokeDashoffset: circ }} animate={{ strokeDashoffset: circ - (circ * score) / 100 }}
          transition={{ duration: 1.5, ease: "easeOut" }} />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ marginTop: 50 }}>
        <span className="text-5xl font-black" style={{ color: catColor }}><AnimatedCounter value={score} /></span>
        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mt-1">{category}</span>
      </div>
    </div>
  );
}

function FindingCard({ finding, index }: { finding: Finding; index: number }) {
  const [open, setOpen] = useState(false);
  const iconBg = finding.severity === "Critical" ? "bg-red-100 text-red-600" : finding.severity === "High" ? "bg-orange-100 text-orange-600" : finding.severity === "Medium" ? "bg-yellow-100 text-yellow-700" : "bg-blue-100 text-blue-600";
  const sevBg = finding.severity === "Critical" ? "bg-red-500" : finding.severity === "High" ? "bg-orange-500" : finding.severity === "Medium" ? "bg-yellow-500" : "bg-blue-500";
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.08 }}
      className="bg-card border border-border hover:border-primary/30 transition-all rounded-2xl overflow-hidden">
      <div className="p-5 cursor-pointer" onClick={() => setOpen(!open)}>
        <div className="flex items-start gap-4">
          <div className={`p-2.5 rounded-xl ${iconBg} shrink-0`}><AlertTriangle className="w-5 h-5" /></div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full text-white ${sevBg}`}>{finding.severity}</span>
              <span className="text-xs text-muted-foreground font-mono">{finding.rule_id}</span>
              <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium ml-auto">Confidence: {finding.confidence}%</span>
            </div>
            <h4 className="text-base font-bold">{finding.title}</h4>
            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{finding.description}</p>
          </div>
          <div className="shrink-0 pt-1">{open ? <ChevronDown className="w-5 h-5 text-muted-foreground" /> : <ChevronRight className="w-5 h-5 text-muted-foreground" />}</div>
        </div>
      </div>
      <AnimatePresence>{open && (
        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="border-t border-border">
          <div className="p-5 space-y-4 bg-muted/20">
            <div><p className="text-xs font-bold uppercase text-muted-foreground mb-1">Resource</p><p className="text-sm font-mono bg-muted px-3 py-2 rounded-lg">{finding.resource_type}.{finding.resource_name}</p></div>
            <div><p className="text-xs font-bold uppercase text-muted-foreground mb-1">Evidence</p><p className="text-sm font-mono bg-muted px-3 py-2 rounded-lg">{finding.evidence}</p></div>
            <div><p className="text-xs font-bold uppercase text-muted-foreground mb-1">Remediation</p><p className="text-sm text-green-700 flex items-start gap-2"><CheckCircle className="w-4 h-4 mt-0.5 shrink-0" />{finding.remediation}</p></div>
            {finding.remediation_code && <div><p className="text-xs font-bold uppercase text-muted-foreground mb-1">Secure Configuration</p><pre className="text-xs bg-foreground/5 border border-border p-3 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono">{finding.remediation_code}</pre></div>}
            <div className="flex flex-wrap gap-2">{finding.compliance_mappings.map((m, i) => (
              <span key={i} className="text-[10px] font-bold bg-primary/5 text-primary border border-primary/20 px-2.5 py-1 rounded-lg">{m.framework}: {m.control_id}</span>
            ))}</div>
          </div>
        </motion.div>
      )}</AnimatePresence>
    </motion.div>
  );
}

function AttackChainViz({ chains }: { chains: AttackChain[] }) {
  if (!chains.length) return null;
  return (
    <div className="space-y-4">
      {chains.map((chain, ci) => (
        <motion.div key={ci} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: ci * 0.15 }}
          className="bg-destructive/5 border border-destructive/20 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-1"><GitBranch className="w-5 h-5 text-destructive" /><h4 className="font-bold text-destructive">{chain.name}</h4></div>
          <p className="text-xs text-destructive/70 font-medium mb-4">{chain.risk_level} Risk</p>
          <div className="flex items-center gap-1 flex-wrap mb-4">
            {chain.steps.map((step, si) => (
              <React.Fragment key={si}>
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: ci * 0.15 + si * 0.1 }}
                  className={`text-xs px-3 py-1.5 rounded-lg font-medium border ${step.severity === "Critical" ? "bg-red-100 border-red-300 text-red-800" : step.severity === "High" ? "bg-orange-100 border-orange-300 text-orange-800" : "bg-yellow-100 border-yellow-300 text-yellow-800"}`}>
                  {step.title}
                </motion.div>
                {si < chain.steps.length - 1 && <ChevronRight className="w-4 h-4 text-destructive/40 shrink-0" />}
              </React.Fragment>
            ))}
          </div>
          <p className="text-sm text-muted-foreground">{chain.description}</p>
          {chain.business_impact && <p className="text-xs text-destructive/80 mt-2 font-medium italic">{chain.business_impact}</p>}
        </motion.div>
      ))}
    </div>
  );
}

function ComplianceBars({ compliance }: { compliance: ComplianceStatus[] }) {
  return (
    <div className="space-y-4">
      {compliance.map((c, i) => (
        <div key={i}>
          <div className="flex justify-between mb-1.5"><span className="text-sm font-semibold">{c.framework}</span><span className="text-sm font-bold" style={{ color: COMP_COLORS[i] }}>{c.percentage}%</span></div>
          <div className="h-3 bg-muted rounded-full overflow-hidden">
            <motion.div initial={{ width: 0 }} animate={{ width: `${c.percentage}%` }} transition={{ duration: 1, delay: i * 0.2 }}
              className="h-full rounded-full" style={{ backgroundColor: COMP_COLORS[i] }} />
          </div>
          <p className="text-[10px] text-muted-foreground mt-1">{c.passed}/{c.total_controls} controls passed · {c.failed} violations</p>
        </div>
      ))}
    </div>
  );
}

type Tab = "dashboard" | "findings" | "chains" | "compliance";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");
  const [showLanding, setShowLanding] = useState(true);

  const handleGoHome = useCallback(() => {
    setShowLanding(true);
    setFile(null);
    setResults(null);
    setError(null);
    setActiveTab("dashboard");
  }, []);

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]; if (!f) return;
    setFile(f); setLoading(true); setError(null); setResults(null);
    try { const data = await auditFile(f); setResults(data); setActiveTab("dashboard"); }
    catch (err: any) { setError(err?.response?.data?.detail || "Audit failed. Ensure the backend is running on port 8000."); }
    finally { setLoading(false); }
  }, []);

  const sevData = results ? Object.entries(results.posture.severity_breakdown).filter(([, v]) => v > 0).map(([k, v]) => ({ name: k, value: v, color: SEV_COLORS[k] || "#888" })) : [];
  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: "dashboard", label: "Dashboard", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "findings", label: "Findings", icon: <Eye className="w-4 h-4" /> },
    { id: "chains", label: "Attack Chains", icon: <GitBranch className="w-4 h-4" /> },
    { id: "compliance", label: "Compliance", icon: <Lock className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <AnimatePresence mode="wait">
        {showLanding ? (
          <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -20 }} className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-background">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />
            <div className="z-10 text-center max-w-3xl px-6">
              <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }} className="inline-flex items-center justify-center p-4 bg-primary/10 rounded-3xl mb-8 shadow-[0_0_30px_-5px_rgba(124,58,237,0.3)]">
                <Shield className="w-20 h-20 text-primary" />
              </motion.div>
              <motion.h1 initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1, duration: 0.5 }} className="text-5xl md:text-7xl font-black tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                VibeGuard Enterprise
              </motion.h1>
              <motion.p initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2, duration: 0.5 }} className="text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed">
                AI-Powered Infrastructure Security Auditor. Scan, analyze, and remediate Terraform vulnerabilities in seconds using deterministic rules and Gemini AI contextual reasoning.
              </motion.p>
              <motion.button initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3, duration: 0.5 }} onClick={() => setShowLanding(false)} className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-2xl text-lg font-bold hover:scale-105 transition-all shadow-[0_0_40px_-10px_rgba(124,58,237,0.5)]">
                Launch Auditor <ArrowRight className="w-5 h-5" />
              </motion.button>
            </div>
            <div className="absolute top-1/4 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute bottom-1/4 right-10 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          </motion.div>
        ) : (
          <motion.div key="app" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen flex flex-col">
            {/* ── Header ── */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-xl border-b border-border">
        <div className="max-w-[1400px] mx-auto px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer group" onClick={handleGoHome}>
              <div className="p-2 bg-primary/10 rounded-xl group-hover:bg-primary/20 transition-colors"><Shield className="w-7 h-7 text-primary" /></div>
              <div><h1 className="text-xl font-bold tracking-tight">VibeGuard</h1><p className="text-[11px] text-muted-foreground font-medium">AI-Powered Security Auditor</p></div>
            </div>
          <div className="flex items-center gap-6">
            {results && (
              <nav className="hidden md:flex items-center gap-1 bg-muted/50 rounded-xl p-1">
                {tabs.map(t => (
                  <button key={t.id} onClick={() => setActiveTab(t.id)}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${activeTab === t.id ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}>
                    {t.icon}{t.label}
                  </button>
                ))}
              </nav>
            )}
            <div className="flex items-center gap-2 text-xs"><span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /><span className="font-medium text-muted-foreground">Online</span></div>
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-8">
        {/* ── Upload Section ── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="bg-card border border-border rounded-2xl p-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div><h2 className="text-lg font-bold flex items-center gap-2"><Upload className="w-5 h-5 text-primary" />Infrastructure Audit</h2><p className="text-sm text-muted-foreground mt-0.5">Upload a Terraform (.tf) file for security analysis</p></div>
              <div className="relative">
                <input type="file" onChange={handleUpload} accept=".tf" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" id="file-upload" />
                <label htmlFor="file-upload" className="flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-semibold cursor-pointer hover:opacity-90 transition-opacity shadow-sm">
                  <FileText className="w-4 h-4" />{file ? file.name : "Select .tf File"}
                </label>
              </div>
            </div>
            {loading && <div className="mt-4 flex items-center gap-2 text-primary"><Activity className="w-4 h-4 animate-spin" /><span className="text-sm font-medium">Running security analysis pipeline...</span></div>}
            {error && <p className="mt-4 text-sm text-destructive font-medium">{error}</p>}
          </div>
        </motion.div>

        {/* ── Empty State ── */}
        {!results && !loading && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 3 }} className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mb-6">
              <Zap className="w-9 h-9 text-muted-foreground" />
            </motion.div>
            <h3 className="text-2xl font-bold mb-2">Ready for Audit</h3>
            <p className="text-muted-foreground max-w-md">Upload a Terraform configuration to begin deterministic scanning, AI contextual reasoning, and attack chain correlation.</p>
          </div>
        )}

        {/* ── Results ── */}
        {results && (
          <AnimatePresence mode="wait">
            {/* Dashboard Tab */}
            {activeTab === "dashboard" && (
              <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-8">
                {/* Stat Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "Risk Score", value: results.posture.overall, color: results.posture.overall >= 81 ? "#dc2626" : results.posture.overall >= 51 ? "#ea580c" : "#d97706", suffix: "/100" },
                    { label: "Total Findings", value: results.posture.total_findings, color: "#7c3aed" },
                    { label: "Critical", value: results.posture.severity_breakdown.Critical || 0, color: "#dc2626" },
                    { label: "Attack Chains", value: results.attack_chains.length, color: "#ea580c" },
                  ].map((s, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                      className="bg-card border border-border rounded-2xl p-5">
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">{s.label}</p>
                      <p className="text-3xl font-black" style={{ color: s.color }}><AnimatedCounter value={s.value} suffix={s.suffix || ""} /></p>
                    </motion.div>
                  ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Posture Gauge */}
                  <div className="bg-card border border-border rounded-2xl p-6 flex flex-col items-center">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-4">Security Posture</h3>
                    <div className="relative"><PostureGauge score={results.posture.overall} category={results.posture.risk_category} /></div>
                    <p className="text-xs text-muted-foreground text-center mt-6 italic max-w-xs">
                      {results.posture.overall >= 81 ? "Critical risk detected. Immediate action required." : results.posture.overall >= 51 ? "High risk infrastructure. Remediation recommended." : results.posture.overall >= 21 ? "Moderate risk. Review flagged items." : "Good security posture."}
                    </p>
                  </div>

                  {/* Severity Distribution */}
                  <div className="bg-card border border-border rounded-2xl p-6">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-4">Severity Distribution</h3>
                    <div className="h-56">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={sevData} innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value" animationDuration={1000}>
                            {sevData.map((e, i) => <Cell key={i} fill={e.color} />)}
                          </Pie>
                          <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e5e7eb", fontSize: 12 }} />
                          <Legend wrapperStyle={{ fontSize: 11 }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Compliance Overview */}
                  <div className="bg-card border border-border rounded-2xl p-6">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-4">Compliance Status</h3>
                    <ComplianceBars compliance={results.compliance} />
                  </div>
                </div>

                {/* AI Executive Summary */}
                {results.ai_analysis && (
                    <div className="bg-gradient-to-br from-primary/5 to-accent/10 border border-primary/10 rounded-2xl p-8">
                      <h3 className="text-lg font-bold flex items-center gap-2 mb-4"><Zap className="w-5 h-5 text-primary" />AI Executive Summary</h3>
                      <div className="text-sm text-foreground/80 leading-relaxed markdown-content">
                        <ReactMarkdown>{results.ai_analysis.executive_summary}</ReactMarkdown>
                      </div>
                    </div>
                )}

                {/* Posture Timeline (Before/After) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-card border border-border rounded-2xl p-6 text-center">
                    <p className="text-xs font-bold uppercase text-muted-foreground mb-2">Current Posture</p>
                    <p className="text-4xl font-black text-destructive"><AnimatedCounter value={results.posture.overall} /><span className="text-lg">/100 risk</span></p>
                  </div>
                  <div className="bg-card border border-border rounded-2xl p-6 text-center">
                    <p className="text-xs font-bold uppercase text-muted-foreground mb-2">After Remediation (Projected)</p>
                    <p className="text-4xl font-black text-green-600"><AnimatedCounter value={Math.max(0, Math.round(results.posture.overall * 0.15))} /><span className="text-lg">/100 risk</span></p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Findings Tab */}
            {activeTab === "findings" && (
              <motion.div key="findings" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-xl font-bold">Vulnerability Report</h2>
                  <span className="text-sm text-muted-foreground font-medium">{results.findings.length} findings</span>
                </div>
                {results.findings.map((f, i) => <FindingCard key={f.id} finding={f} index={i} />)}
                {results.ai_analysis && (
                    <div className="bg-card border border-border rounded-2xl p-6 mt-6 space-y-4">
                      <h3 className="text-lg font-bold flex items-center gap-2"><Zap className="w-5 h-5 text-primary" />AI Technical Analysis</h3>
                      <div className="text-sm text-muted-foreground leading-relaxed markdown-content">
                        <ReactMarkdown>{results.ai_analysis.technical_analysis}</ReactMarkdown>
                      </div>
                      <h4 className="text-base font-bold mt-4">Business Impact</h4>
                      <div className="text-sm text-muted-foreground leading-relaxed markdown-content">
                        <ReactMarkdown>{results.ai_analysis.business_impact}</ReactMarkdown>
                      </div>
                      <h4 className="text-base font-bold mt-4">Remediation Plan</h4>
                      <div className="text-sm text-muted-foreground leading-relaxed markdown-content">
                        <ReactMarkdown>{results.ai_analysis.remediation_plan}</ReactMarkdown>
                      </div>
                    </div>
                )}
              </motion.div>
            )}

            {/* Attack Chains Tab */}
            {activeTab === "chains" && (
              <motion.div key="chains" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <h2 className="text-xl font-bold mb-4">Risk Correlation — Attack Chains</h2>
                {results.attack_chains.length > 0 ? <AttackChainViz chains={results.attack_chains} /> : <p className="text-muted-foreground text-center py-12">No correlated attack chains detected.</p>}
              </motion.div>
            )}

            {/* Compliance Tab */}
            {activeTab === "compliance" && (
              <motion.div key="compliance" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <h2 className="text-xl font-bold mb-6">Compliance Dashboard</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {results.compliance.map((c, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                      className="bg-card border border-border rounded-2xl p-6">
                      <h3 className="text-lg font-bold mb-1" style={{ color: COMP_COLORS[i] }}>{c.framework}</h3>
                      <p className="text-4xl font-black mt-2" style={{ color: COMP_COLORS[i] }}>{c.percentage}%</p>
                      <p className="text-xs text-muted-foreground mt-1">Compliant</p>
                      <div className="h-2.5 bg-muted rounded-full overflow-hidden mt-4">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${c.percentage}%` }} transition={{ duration: 1 }} className="h-full rounded-full" style={{ backgroundColor: COMP_COLORS[i] }} />
                      </div>
                      <div className="flex justify-between mt-3 text-xs text-muted-foreground">
                        <span>{c.passed} passed</span><span>{c.failed} failed</span><span>{c.total_controls} total</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="bg-card border border-border rounded-2xl p-6 mt-6">
                  <h3 className="text-base font-bold mb-4">Compliance Violation Details</h3>
                  <div className="space-y-2">
                    {results.findings.flatMap(f => f.compliance_mappings.map(m => ({ ...m, finding: f.title, severity: f.severity }))).map((item, i) => (
                      <div key={i} className="flex items-center justify-between py-2 px-3 bg-muted/30 rounded-lg text-sm">
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-bold bg-primary/10 text-primary px-2 py-0.5 rounded">{item.framework} {item.control_id}</span>
                          <span className="text-muted-foreground">{item.finding}</span>
                        </div>
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full text-white ${item.severity === "Critical" ? "bg-red-500" : item.severity === "High" ? "bg-orange-500" : "bg-yellow-500"}`}>{item.severity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </main>

      <footer className="mt-auto border-t border-border py-4 text-center text-xs text-muted-foreground">VibeGuard v1.0 — AI-Powered Enterprise Security Auditor</footer>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
