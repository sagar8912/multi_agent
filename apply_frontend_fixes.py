import os

base_path = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer"
frontend_path = os.path.join(base_path, "frontend")

files = {}

files[os.path.join(frontend_path, "src", "styles", "App.css")] = """\
:root {
  --bg-color: #f8fafc;
  --header-bg: #0f172a;
  --header-text: #f8fafc;
  --card-bg: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --accent-blue: #3b82f6;
  --accent-hover: #2563eb;
  --border-color: #e2e8f0;
  
  --risk-very-fav: #10b981;
  --risk-fav: #3b82f6;
  --risk-avg: #eab308;
  --risk-part-unfav: #f97316;
  --risk-unfav: #ef4444;
  --risk-unknown: #94a3b8;
}

body {
  margin: 0;
  font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: var(--header-bg);
  color: var(--header-text);
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.header p {
  margin: 0;
  color: #cbd5e1;
  font-size: 1.1rem;
}

.main-content {
  padding: 2rem;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -4px rgba(0,0,0,0.05);
  border: 1px solid var(--border-color);
}

.card h2 {
  margin-top: 0;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-main);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.form-group label {
  font-weight: 600;
  font-size: 0.9rem;
}
.form-group input, .form-group select {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 1rem;
  background: #f8fafc;
  transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: var(--accent-blue);
  background: #ffffff;
}

.btn {
  background-color: var(--accent-blue);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.btn:hover:not(:disabled) { background-color: var(--accent-hover); color: white; transform: translateY(-1px); }
.btn:disabled { background-color: #cbd5e1; cursor: not-allowed; transform: none; }
.btn-outline {
  background-color: transparent;
  color: var(--accent-blue);
  border: 1px solid var(--accent-blue);
}
.btn-outline:hover:not(:disabled) {
  background-color: #eff6ff;
  color: var(--accent-hover);
}

.demo-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.demo-btn {
  background: #f1f5f9;
  border: 1px solid var(--border-color);
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--text-muted);
  font-weight: 500;
  transition: all 0.2s;
}
.demo-btn:hover { background: #e2e8f0; color: var(--text-main); }

.error-banner {
  background-color: #fef2f2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #f87171;
  font-weight: 600;
  text-align: center;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.85rem;
  color: white;
  display: inline-block;
}

.risk-meter {
  display: flex;
  gap: 4px;
  margin: 1rem 0 2rem 0;
  border-radius: 20px;
}
.risk-meter-block {
  flex: 1;
  text-align: center;
  padding: 0.5rem;
  font-size: 0.85rem;
  font-weight: bold;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.risk-meter-block.active { opacity: 1; transform: scaleY(1.15); z-index: 10; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; }

.risk-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-stat {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
th, td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}
th { background-color: #f8fafc; font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em; }
tr:last-child td { border-bottom: none; }
tr:hover td { background-color: #f8fafc; }

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}
.loading-steps {
  margin-top: 2rem;
  text-align: left;
  color: var(--text-muted);
  list-style: none;
  padding: 0;
  font-size: 1.1rem;
}
.loading-steps li { margin: 0.75rem 0; display: flex; align-items: center; gap: 0.5rem; }

.report-item {
  background: #ffffff;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.report-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}
.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.3s ease-out;
}
.modal-close {
  position: absolute;
  top: 1rem; right: 1rem;
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.2s;
}
.modal-close:hover { background: #e2e8f0; color: var(--text-main); }

/* Toasts */
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.toast {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.toast.success { background-color: #10b981; }
.toast.error { background-color: #ef4444; }

.footer {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
  background: white;
}
"""

files[os.path.join(frontend_path, "src", "components", "CompanyForm.jsx")] = """\
import React, { useState } from 'react';

export default function CompanyForm({ onSubmit, loading, disabled }) {
  const [formData, setFormData] = useState({
    company_name: '',
    domain: '',
    country: '',
    revenue_band: '> $1B',
    industry: ''
  });
  const [error, setError] = useState('');

  const demos = [
    { label: "Microsoft", data: { company_name: "Microsoft", domain: "microsoft.com", country: "USA", revenue_band: "> $1B", industry: "Technology" } },
    { label: "Apple", data: { company_name: "Apple", domain: "apple.com", country: "USA", revenue_band: "> $1B", industry: "Technology" } },
    { label: "OpenAI", data: { company_name: "OpenAI", domain: "openai.com", country: "USA", revenue_band: "Unknown", industry: "Artificial Intelligence" } },
    { label: "ChatGPT", data: { company_name: "ChatGPT", domain: "https://chatgpt.com/", country: "USA", revenue_band: "> $1B", industry: "Artificial Intelligence" } },
    { label: "Example.com", data: { company_name: "Example", domain: "example.com", country: "USA", revenue_band: "< $50M", industry: "Other" } }
  ];

  const fillDemo = (data) => {
    setFormData(data);
    setError('');
  };

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.company_name || !formData.domain || !formData.country) {
      setError('Company Name, Domain, and Country are required.');
      return;
    }
    setError('');
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2>Analyze Company</h2>
      
      <div className="demo-buttons">
        <span style={{fontSize:'0.85rem', color:'#64748b', alignSelf:'center', fontWeight:600}}>Quick Demo:</span>
        {demos.map(d => (
          <button key={d.label} type="button" className="demo-btn" onClick={() => fillDemo(d.data)}>{d.label}</button>
        ))}
      </div>

      {error && <p style={{color: '#dc2626', fontSize: '0.9rem', fontWeight:600}}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Company Name *</label>
          <input name="company_name" value={formData.company_name} onChange={handleChange} placeholder="e.g. Acme Corp" />
        </div>
        <div className="form-group">
          <label>Domain *</label>
          <input name="domain" value={formData.domain} onChange={handleChange} placeholder="e.g. acme.com or https://acme.com" />
        </div>
        <div className="form-group">
          <label>Country *</label>
          <input name="country" value={formData.country} onChange={handleChange} placeholder="e.g. USA" />
        </div>
        <div className="form-group">
          <label>Revenue Band</label>
          <select name="revenue_band" value={formData.revenue_band} onChange={handleChange}>
            <option>&gt; $1B</option>
            <option>$250M - $1B</option>
            <option>$50M - $250M</option>
            <option>&lt; $50M</option>
            <option>Unknown</option>
          </select>
        </div>
        <div className="form-group">
          <label>Industry</label>
          <input name="industry" value={formData.industry} onChange={handleChange} />
        </div>
        
        <button type="submit" className="btn" style={{width:'100%', marginTop:'1rem'}} disabled={disabled || loading}>
          {loading ? 'Running Cyber Risk Agents...' : 'Run Agentic Analysis'}
        </button>
      </form>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "RiskSummary.jsx")] = """\
import React from 'react';
import { downloadJsonUrl, downloadPdfUrl } from '../api/cyberRiskApi';

export const getBadgeColor = (category) => {
  switch(category) {
    case 'Very Favorable': return 'var(--risk-very-fav)';
    case 'Favorable': return 'var(--risk-fav)';
    case 'Average': return 'var(--risk-avg)';
    case 'Partially Unfavorable': return 'var(--risk-part-unfav)';
    case 'Unfavorable': return 'var(--risk-unfav)';
    default: return 'var(--risk-unknown)';
  }
};

export const Badge = ({ category }) => (
  <span className="badge" style={{ backgroundColor: getBadgeColor(category) }}>
    {category}
  </span>
);

export default function RiskSummary({ report, addToast }) {
  if (!report) return null;

  const categories = [
    { label: "Very Favorable", val: "Very Favorable", color: "var(--risk-very-fav)" },
    { label: "Favorable", val: "Favorable", color: "var(--risk-fav)" },
    { label: "Average", val: "Average", color: "var(--risk-avg)" },
    { label: "Partially Unfav", val: "Partially Unfavorable", color: "var(--risk-part-unfav)" },
    { label: "Unfavorable", val: "Unfavorable", color: "var(--risk-unfav)" }
  ];
  
  const domainMod = report.modifiers.find(m => m.modifier_name === 'Domain Encryption');
  const normalizedDomain = domainMod?.raw_data?.normalized_domain || report.domain;

  return (
    <div>
      {/* Company Details Card */}
      <div className="card" style={{marginBottom: '2rem'}}>
        <h2 style={{borderBottom:'none', margin:0, marginBottom:'1rem'}}>Company Details</h2>
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(250px, 1fr))', gap:'1.5rem', fontSize:'0.95rem'}}>
          <div><strong style={{color:'var(--text-muted)'}}>Company</strong><br/><span style={{fontSize:'1.1rem', fontWeight:600}}>{report.company_name}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Input Domain</strong><br/><span style={{fontSize:'1.1rem'}}>{report.domain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Normalized Domain</strong><br/><span style={{fontSize:'1.1rem', color:'var(--accent-blue)', fontWeight:600}}>{normalizedDomain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Country</strong><br/><span style={{fontSize:'1.1rem'}}>{report.country}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Revenue Band</strong><br/><span style={{fontSize:'1.1rem'}}>{report.revenue_band}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Industry</strong><br/><span style={{fontSize:'1.1rem'}}>{report.industry || 'N/A'}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Report Generated At</strong><br/><span>{new Date(report.generated_at).toLocaleString()}</span></div>
        </div>
      </div>

      <div className="card">
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'1rem'}}>
          <h2 style={{border:'none', margin:0}}>Overall Cyber Risk Profile</h2>
          {report.report_filename && (
            <div style={{display:'flex', gap:'0.5rem'}}>
              <a href={downloadJsonUrl(report.report_filename)} className="btn btn-outline" download onClick={() => addToast('JSON downloaded successfully')}>Download JSON</a>
              <a href={downloadPdfUrl(report.report_filename)} className="btn" target="_blank" rel="noreferrer" onClick={() => addToast('PDF downloaded successfully')}>Download PDF</a>
            </div>
          )}
        </div>

        <div style={{textAlign:'center', marginTop:'2rem', marginBottom:'0.5rem', fontWeight:600, fontSize:'1.1rem'}}>
          Current Position: <span style={{color: getBadgeColor(report.overall_risk_category)}}>{report.overall_risk_category}</span>
        </div>
        
        <div className="risk-meter" style={{height:'40px', borderRadius:'8px', overflow:'hidden', position:'relative'}}>
          {categories.map(c => (
            <div key={c.label} 
                 className={`risk-meter-block ${report.overall_risk_category === c.val ? 'active' : ''}`}
                 style={{ 
                   backgroundColor: c.color, 
                   opacity: report.overall_risk_category === c.val ? 1 : 0.4,
                   display: 'flex', flexDirection: 'column', alignItems:'center', justifyContent:'center',
                 }}>
              {c.label}
            </div>
          ))}
        </div>
        {/* Triangle marker */}
        <div style={{display:'flex', height:'10px'}}>
          {categories.map(c => (
            <div key={c.label} style={{flex:1, display:'flex', justifyContent:'center'}}>
              {report.overall_risk_category === c.val && (
                 <div style={{width:0, height:0, borderLeft:'10px solid transparent', borderRight:'10px solid transparent', borderTop:`10px solid ${c.color}`}}></div>
              )}
            </div>
          ))}
        </div>
        
        <div className="risk-summary-grid" style={{marginTop:'2rem'}}>
          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Overall Score</span>
            <div style={{fontSize:'3rem', fontWeight:'800', color: 'var(--text-main)'}}>{report.overall_score?.toFixed(2)}</div>
          </div>
          
          {/* Big Risk Category Card */}
          <div className="summary-stat" style={{backgroundColor: getBadgeColor(report.overall_risk_category), color:'white', border:'none', display:'flex', flexDirection:'column', justifyContent:'center'}}>
            <span style={{fontSize:'0.9rem', opacity:0.9, textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Risk Category</span>
            <div style={{fontSize:'2.2rem', fontWeight:'800', marginTop:'0.5rem', lineHeight:1.2}}>{report.overall_risk_category}</div>
          </div>

          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Confidence</span>
            <div style={{fontSize:'3rem', fontWeight:'800', color: 'var(--text-main)'}}>{(report.overall_confidence * 100).toFixed(0)}%</div>
          </div>
          
          <div className="summary-stat" style={{gridColumn: '1 / -1', textAlign:'left', padding:'2rem'}}>
            <h3 style={{margin:'0 0 1rem 0', fontSize:'1.2rem', color:'var(--text-main)'}}>Underwriter Summary</h3>
            <p style={{margin:0, whiteSpace:'pre-wrap', lineHeight:1.6, color:'var(--text-main)', fontSize:'1.05rem'}}>{report.underwriter_summary}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "ModifierDetails.jsx")] = """\
import React from 'react';
import { getBadgeColor } from './RiskSummary';

export default function ModifierDetails({ mod }) {
  if (!mod) return null;
  return (
    <div>
      <h2 style={{marginTop:0, marginBottom:'1rem', fontSize:'1.8rem', color:'var(--text-main)'}}>{mod.modifier_name} Assessment</h2>
      
      <div style={{display:'flex', gap:'1rem', marginBottom:'2rem', flexWrap:'wrap'}}>
        <span className="badge" style={{background: '#1e293b', fontSize:'1rem'}}>Score: {mod.score}</span>
        <span className="badge" style={{background: getBadgeColor(mod.risk_category), fontSize:'1rem'}}>{mod.risk_category}</span>
        <span className="badge" style={{background: '#3b82f6', fontSize:'1rem'}}>Confidence: {(mod.confidence*100).toFixed(0)}%</span>
        <span className="badge" style={{background: mod.verification_status === 'verified' ? '#10b981' : mod.verification_status === 'partially_verified' ? '#f59e0b' : '#ef4444', fontSize:'1rem'}}>
          Status: {mod.verification_status || 'Unknown'}
        </span>
      </div>

      <h3 style={{color:'var(--text-muted)', borderBottom:'1px solid var(--border-color)', paddingBottom:'0.5rem'}}>Findings</h3>
      <ul style={{fontSize:'1.05rem', lineHeight:1.6, marginBottom:'2rem'}}>
        {mod.findings.map((f, i) => <li key={i}>{f}</li>)}
      </ul>
      
      {mod.evidence && mod.evidence.length > 0 && (
        <>
          <h3 style={{color:'var(--text-muted)', borderBottom:'1px solid var(--border-color)', paddingBottom:'0.5rem'}}>Verified Evidence</h3>
          <ul style={{fontSize:'1rem', lineHeight:1.6, marginBottom:'2rem'}}>
            {mod.evidence.map((ev, i) => (
              <li key={i} style={{marginBottom:'0.5rem'}}>
                <strong>{ev.description}</strong>
                {ev.url && <span> - <a href={ev.url} target="_blank" rel="noreferrer" style={{color:'var(--accent-blue)', textDecoration:'none', fontWeight:600}}>{ev.url}</a></span>}
                {ev.status_code && <span style={{color:'var(--text-muted)'}}> (Status: {ev.status_code})</span>}
              </li>
            ))}
          </ul>
        </>
      )}

      {mod.recommendation && (
        <>
          <h3 style={{color:'var(--text-muted)', borderBottom:'1px solid var(--border-color)', paddingBottom:'0.5rem'}}>Mitigation Recommendation</h3>
          <p style={{background:'#eff6ff', padding:'1rem', borderRadius:'8px', color:'#1e40af', margin:0, fontWeight:500, fontSize:'1.05rem', borderLeft:'4px solid #3b82f6'}}>
            {mod.recommendation}
          </p>
        </>
      )}
      
      {mod.raw_data && (
        <>
          <h3 style={{color:'var(--text-muted)', borderBottom:'1px solid var(--border-color)', paddingBottom:'0.5rem', marginTop:'2rem'}}>Backend Raw Data</h3>
          <pre style={{background:'#f1f5f9', padding:'1.5rem', borderRadius:'8px', fontSize:'0.9rem', overflowX:'auto', border:'1px solid var(--border-color)'}}>
            {JSON.stringify(mod.raw_data, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "ReportsList.jsx")] = """\
import React, { useState, useEffect } from 'react';
import { getReports, downloadJsonUrl, downloadPdfUrl } from '../api/cyberRiskApi';

export default function ReportsList({ onSelectReport, addToast }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await getReports();
      setReports(data.saved_reports || []);
    } catch (err) {} finally { setLoading(false); }
  };

  useEffect(() => { fetchReports(); }, []);

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.5rem'}}>
        <h2 style={{border:'none', margin:0}}>Saved Reports</h2>
        <button onClick={fetchReports} className="btn btn-outline" style={{padding:'0.4rem 0.8rem', fontSize:'0.85rem'}}>Refresh List</button>
      </div>
      
      {loading && <p>Loading reports...</p>}
      {!loading && reports.length === 0 && <p style={{color:'var(--text-muted)'}}>No reports generated yet.</p>}
      
      <div style={{display:'flex', flexDirection:'column', gap:'0.75rem', maxHeight:'500px', overflowY:'auto', paddingRight:'0.5rem'}}>
        {reports.map((filename, i) => (
          <div key={i} className="report-item">
            <span style={{fontWeight:600, fontSize:'0.9rem', wordBreak:'break-all'}}>{filename}</span>
            <div className="report-actions" style={{display:'flex', gap:'0.5rem', flexWrap:'wrap', justifyContent:'flex-end'}}>
              <button onClick={() => onSelectReport(filename)} className="btn" style={{padding:'0.3rem 0.6rem', fontSize:'0.8rem'}}>View</button>
              <a href={downloadJsonUrl(filename)} className="btn btn-outline" style={{padding:'0.3rem 0.6rem', fontSize:'0.8rem'}} download onClick={() => addToast('JSON downloaded successfully')}>JSON</a>
              <a href={downloadPdfUrl(filename)} className="btn btn-outline" style={{padding:'0.3rem 0.6rem', fontSize:'0.8rem'}} target="_blank" rel="noreferrer" onClick={() => addToast('PDF downloaded successfully')}>PDF</a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "App.jsx")] = """\
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CompanyForm from './components/CompanyForm';
import RiskSummary, { Badge, getBadgeColor } from './components/RiskSummary';
import ModifierDetails from './components/ModifierDetails';
import ReportsList from './components/ReportsList';
import { checkHealth, analyzeCompany, getReportByFilename } from './api/cyberRiskApi';

function App() {
  const [isHealthy, setIsHealthy] = useState(true);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [selectedMod, setSelectedMod] = useState(null);
  const [toasts, setToasts] = useState([]);

  const addToast = (msg, type='success') => {
    const id = Date.now();
    setToasts(p => [...p, {id, msg, type}]);
    setTimeout(() => setToasts(p => p.filter(t => t.id !== id)), 3000);
  };

  useEffect(() => {
    checkHealth().then(() => setIsHealthy(true)).catch(() => {
      setIsHealthy(false);
      addToast('Backend not reachable', 'error');
    });
  }, []);

  const handleAnalyze = async (formData) => {
    setLoading(true); setReport(null);
    try {
      const data = await analyzeCompany(formData);
      setReport(data);
      addToast('Report generated successfully');
    } catch (err) {
      addToast('Something went wrong generating report', 'error');
    } finally { setLoading(false); }
  };

  const handleSelectReport = async (filename) => {
    setLoading(true); setReport(null);
    try {
      const data = await getReportByFilename(filename);
      setReport(data);
      addToast('Report loaded successfully');
    } catch (err) {
      addToast('Something went wrong loading report', 'error');
    } finally { setLoading(false); }
  };

  return (
    <div className="app-container">
      <Header />
      
      {!isHealthy && (
        <div style={{padding: '1rem 2rem'}}>
          <div className="error-banner">Backend is not reachable. Please start FastAPI server using python run.py.</div>
        </div>
      )}

      <main className="main-content">
        <div style={{display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(300px, 1fr)', gap: '2rem', alignItems: 'start'}}>
          <CompanyForm onSubmit={handleAnalyze} loading={loading} disabled={!isHealthy} />
          <ReportsList onSelectReport={handleSelectReport} addToast={addToast} />
        </div>

        {loading && (
          <div className="card loading-container">
            <h2 style={{border:'none', margin:0, fontSize:'1.8rem', color:'var(--accent-blue)'}}>Running Agentic Cyber Risk Workflow...</h2>
            <ul className="loading-steps">
              <li>⚙️ Normalizing domain and entity resolution</li>
              <li>🔍 Checking HTTPS encryption algorithms</li>
              <li>🛡️ Reviewing privacy policy and GDPR/CCPA presence</li>
              <li>🛒 Detecting e-commerce and checkout exposure</li>
              <li>🏢 Identifying B2B vs B2C customer profile</li>
              <li>🌍 Estimating global geographic spread</li>
              <li>📑 Validating evidence links securely</li>
              <li>🤖 Generating professional underwriter summary</li>
            </ul>
          </div>
        )}

        {report && !loading && (
          <div style={{display:'flex', flexDirection:'column', gap:'2rem', animation: 'fadeIn 0.5s ease'}}>
            <RiskSummary report={report} addToast={addToast} />
            
            <div className="card" style={{overflowX: 'auto'}}>
              <h2 style={{borderBottom:'none'}}>Modifier Assessments</h2>
              <table>
                <thead>
                  <tr>
                    <th>Modifier</th>
                    <th>Score</th>
                    <th>Risk Category</th>
                    <th>Verification</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {report.modifiers.map((mod, idx) => (
                    <tr key={idx}>
                      <td><strong>{mod.modifier_name}</strong></td>
                      <td><span style={{fontWeight:800, fontSize:'1.1rem'}}>{mod.score}</span></td>
                      <td>
                        <span style={{color: getBadgeColor(mod.risk_category), fontWeight:700, display:'flex', alignItems:'center', gap:'0.25rem'}}>
                          <div style={{width:'8px', height:'8px', borderRadius:'50%', background: getBadgeColor(mod.risk_category)}}></div>
                          {mod.risk_category}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          padding:'0.2rem 0.6rem', borderRadius:'99px', fontSize:'0.8rem', fontWeight:700,
                          background: mod.verification_status==='verified' ? '#dcfce7' : mod.verification_status==='partially_verified' ? '#fef3c7' : '#fee2e2',
                          color: mod.verification_status==='verified' ? '#166534' : mod.verification_status==='partially_verified' ? '#92400e' : '#991b1b'
                        }}>
                          {mod.verification_status?.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <button onClick={() => setSelectedMod(mod)} className="btn btn-outline" style={{padding:'0.4rem 1rem', fontSize:'0.85rem'}}>
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        Emerging Risk Identifier | Cyber Risk Module | MVP Demo
      </footer>

      {selectedMod && (
        <div className="modal-overlay" onClick={() => setSelectedMod(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedMod(null)}>&times;</button>
            <ModifierDetails mod={selectedMod} />
          </div>
        </div>
      )}

      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`}>{t.msg}</div>
        ))}
      </div>
    </div>
  );
}

export default App;
"""


def apply():
    for fpath, content in files.items():
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    apply()
