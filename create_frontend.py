import os

frontend_dir = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer\frontend"
backend_main_py = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer\cyber_risk_tool\api\main.py"

def update_backend_cors():
    try:
        with open(backend_main_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "CORSMiddleware" not in content:
            new_content = content.replace("from fastapi import FastAPI\n", "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n")
            
            cors_code = """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
            new_content = new_content.replace('version="1.0.0"\n)', 'version="1.0.0"\n)\n' + cors_code)
            with open(backend_main_py, "w", encoding="utf-8") as f:
                f.write(new_content)
    except Exception as e:
        print(f"Failed to update CORS: {e}")

files = {
"package.json": """{
  "name": "cyber-risk-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}""",
"index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cyber Risk Underwriting Intelligence Tool</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
"vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
""",
"src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/App.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
"src/styles/App.css": """
:root {
  --bg-color: #f4f7f9;
  --header-bg: #0f172a;
  --header-text: #ffffff;
  --card-bg: #ffffff;
  --text-main: #333333;
  --accent-blue: #2563eb;
  --accent-hover: #1d4ed8;
  --border-color: #e2e8f0;
  
  --risk-very-fav: #10b981;
  --risk-fav: #3b82f6;
  --risk-avg: #eab308;
  --risk-part-unfav: #f97316;
  --risk-unfav: #ef4444;
  --risk-unknown: #9ca3af;
}

body {
  margin: 0;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.header p {
  margin: 0.5rem 0 0 0;
  color: #94a3b8;
}

.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid var(--border-color);
}

.card h2 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.healthy { background-color: var(--risk-very-fav); }
.dot.offline { background-color: var(--risk-unfav); }

form {
  display: grid;
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.form-group label {
  font-weight: 600;
  font-size: 0.9rem;
}
.form-group input, .form-group select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
}

button {
  background-color: var(--accent-blue);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
button:hover:not(:disabled) {
  background-color: var(--accent-hover);
}
button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #f87171;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.85rem;
  color: white;
  display: inline-block;
}

.risk-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.summary-stat {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  text-align: center;
}
.summary-stat .label {
  display: block;
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}
.summary-stat .val {
  font-size: 1.5rem;
  font-weight: bold;
}

.summary-text-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}
.summary-text-box p {
  margin-top: 0;
  white-space: pre-wrap;
  line-height: 1.5;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}
th {
  background-color: #f8fafc;
  font-weight: 600;
}

.details-toggle {
  background: none;
  border: none;
  color: var(--accent-blue);
  padding: 0;
  font-weight: normal;
  text-decoration: underline;
}
.details-toggle:hover {
  background: none;
  color: var(--accent-hover);
}
.modifier-details {
  background: #f8fafc;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 6px;
  border-left: 4px solid var(--accent-blue);
}
.modifier-details h4 {
  margin: 0 0 0.5rem 0;
}
.modifier-details ul {
  margin: 0 0 1rem 0;
  padding-left: 1.5rem;
}
.modifier-details li {
  margin-bottom: 0.25rem;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.report-item {
  background: #f8fafc;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.report-item:hover {
  border-color: var(--accent-blue);
  background: #eff6ff;
}
""",
"src/api/cyberRiskApi.js": """import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const checkHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getModifiers = async () => {
  const res = await api.get('/modifiers');
  return res.data;
};

export const analyzeCompany = async (payload) => {
  const res = await api.post('/analyze-company', payload);
  return res.data;
};

export const runModifier = async (modifierName, payload) => {
  const res = await api.post(`/run-modifier/${modifierName}`, payload);
  return res.data;
};

export const getReports = async () => {
  const res = await api.get('/reports');
  return res.data;
};

export const getReportByFilename = async (filename) => {
  const res = await api.get(`/reports/${filename}`);
  return res.data;
};
""",
"src/components/Header.jsx": """import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <h1>Cyber Risk Underwriting Intelligence Tool</h1>
      <p>Agentic AI-based cyber risk assessment for underwriting teams.</p>
    </header>
  );
}
""",
"src/components/StatusCard.jsx": """import React from 'react';

export default function StatusCard({ isHealthy }) {
  return (
    <div className="card">
      <div className="status-indicator">
        Backend Status: 
        {isHealthy ? (
          <><span className="dot healthy"></span> Healthy</>
        ) : (
          <><span className="dot offline"></span> Offline</>
        )}
      </div>
      {!isHealthy && (
        <p className="error-message" style={{marginTop: '1rem', marginBottom: 0}}>
          Unable to connect to backend. Please start FastAPI server using python run.py.
        </p>
      )}
    </div>
  );
}
""",
"src/components/CompanyForm.jsx": """import React, { useState } from 'react';

export default function CompanyForm({ onSubmit, loading, disabled }) {
  const [formData, setFormData] = useState({
    company_name: 'Microsoft',
    domain: 'microsoft.com',
    country: 'USA',
    revenue_band: '> $1B',
    industry: 'Technology'
  });

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2>Company Input</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Company Name</label>
          <input name="company_name" value={formData.company_name} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Domain</label>
          <input name="domain" value={formData.domain} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Country</label>
          <input name="country" value={formData.country} onChange={handleChange} required />
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
        
        <button type="submit" disabled={disabled || loading}>
          {loading ? 'Analyzing company using cyber risk agents...' : 'Analyze Company'}
        </button>
      </form>
    </div>
  );
}
""",
"src/components/RiskSummary.jsx": """import React from 'react';

const getBadgeColor = (category) => {
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

export default function RiskSummary({ report }) {
  if (!report) return null;

  return (
    <div className="card">
      <h2>Overall Cyber Risk Profile</h2>
      
      <div className="risk-summary-grid">
        <div className="summary-stat">
          <span className="label">Company</span>
          <span className="val" style={{fontSize:'1.2rem'}}>{report.company_name}</span>
          <div style={{fontSize:'0.9rem', color:'#666', marginTop:'0.25rem'}}>{report.domain} | {report.country}</div>
        </div>
        
        <div className="summary-stat">
          <span className="label">Overall Score</span>
          <span className="val">{report.overall_score?.toFixed(2)}</span>
        </div>
        
        <div className="summary-stat">
          <span className="label">Risk Category</span>
          <div style={{marginTop: '0.5rem'}}>
            <Badge category={report.overall_risk_category} />
          </div>
        </div>
        
        <div className="summary-stat">
          <span className="label">Confidence</span>
          <span className="val">{(report.overall_confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
      
      <div className="summary-text-box">
        <h3 style={{marginTop:0, marginBottom:'0.5rem', color:'#166534'}}>Underwriter Summary</h3>
        <p style={{color:'#14532d'}}>{report.underwriter_summary}</p>
      </div>
    </div>
  );
}
""",
"src/components/ModifierDetails.jsx": """import React from 'react';

export default function ModifierDetails({ mod }) {
  return (
    <div className="modifier-details">
      <h4>Findings</h4>
      <ul>
        {mod.findings.map((f, i) => <li key={i}>{f}</li>)}
      </ul>
      
      {mod.evidence && mod.evidence.length > 0 && (
        <>
          <h4>Evidence</h4>
          <ul>
            {mod.evidence.map((ev, i) => (
              <li key={i}>
                {ev.description}
                {ev.url && (
                  <> - <a href={ev.url} target="_blank" rel="noreferrer">{ev.url}</a></>
                )}
                {ev.status_code && ` (Status: ${ev.status_code})`}
              </li>
            ))}
          </ul>
        </>
      )}
      
      {mod.raw_data && (
        <>
          <h4>Raw Data</h4>
          <pre style={{background:'#eee', padding:'0.5rem', borderRadius:'4px', fontSize:'0.85rem', overflowX:'auto'}}>
            {JSON.stringify(mod.raw_data, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
}
""",
"src/components/ModifierTable.jsx": """import React, { useState } from 'react';
import { Badge } from './RiskSummary';
import ModifierDetails from './ModifierDetails';

export default function ModifierTable({ modifiers }) {
  const [expanded, setExpanded] = useState({});

  if (!modifiers || modifiers.length === 0) return null;

  const toggle = (name) => {
    setExpanded(prev => ({...prev, [name]: !prev[name]}));
  };

  return (
    <div className="card" style={{overflowX: 'auto'}}>
      <h2>Modifier Assessments</h2>
      <table>
        <thead>
          <tr>
            <th>Modifier</th>
            <th>Score</th>
            <th>Category</th>
            <th>Verified</th>
            <th>Recommendation</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {modifiers.map((mod, idx) => (
            <React.Fragment key={idx}>
              <tr>
                <td><strong>{mod.modifier_name}</strong></td>
                <td>{mod.score}</td>
                <td><Badge category={mod.risk_category} /></td>
                <td>
                  <span style={{
                    color: mod.verification_status === 'verified' ? 'green' : 
                           mod.verification_status === 'partially_verified' ? 'orange' : 'red'
                  }}>
                    {mod.verification_status}
                  </span>
                </td>
                <td style={{fontSize:'0.9rem'}}>{mod.recommendation || '-'}</td>
                <td>
                  <button className="details-toggle" onClick={() => toggle(mod.modifier_name)}>
                    {expanded[mod.modifier_name] ? 'Hide' : 'View'}
                  </button>
                </td>
              </tr>
              {expanded[mod.modifier_name] && (
                <tr>
                  <td colSpan="6" style={{padding: 0, borderBottom: 'none'}}>
                    <ModifierDetails mod={mod} />
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
""",
"src/components/ReportsList.jsx": """import React, { useState, useEffect } from 'react';
import { getReports } from '../api/cyberRiskApi';

export default function ReportsList({ onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await getReports();
      setReports(data.saved_reports || []);
      setError(null);
    } catch (err) {
      setError("Could not load reports");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem', borderBottom:'1px solid #e2e8f0', paddingBottom:'0.5rem'}}>
        <h2 style={{border:'none', padding:0, margin:0}}>Saved Reports</h2>
        <button onClick={fetchReports} style={{padding:'0.4rem 0.8rem', fontSize:'0.9rem'}}>Refresh</button>
      </div>
      
      {loading && <p>Loading reports...</p>}
      {error && <p className="error-message">{error}</p>}
      
      {!loading && !error && reports.length === 0 && <p>No reports found.</p>}
      
      <div className="report-list">
        {reports.map((filename, i) => (
          <div key={i} className="report-item" onClick={() => onSelectReport(filename)}>
            <span>📄 {filename}</span>
            <span style={{color:'var(--accent-blue)'}}>View &rarr;</span>
          </div>
        ))}
      </div>
    </div>
  );
}
""",
"src/components/SingleModifierRunner.jsx": """import React, { useState, useEffect } from 'react';
import { getModifiers, runModifier } from '../api/cyberRiskApi';
import ModifierDetails from './ModifierDetails';
import { Badge } from './RiskSummary';

export default function SingleModifierRunner({ companyData }) {
  const [modifiers, setModifiers] = useState([]);
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getModifiers().then(data => {
      setModifiers(data.enabled_modifiers || []);
      if(data.enabled_modifiers?.length > 0) setSelected(data.enabled_modifiers[0]);
    }).catch(e => console.error(e));
  }, []);

  const handleRun = async () => {
    if(!selected) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await runModifier(selected, companyData);
      setResult(res);
    } catch (err) {
      setError("Failed to run modifier.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Run Single Modifier</h2>
      <div style={{display:'flex', gap:'1rem', alignItems:'center', marginBottom:'1rem'}}>
        <select value={selected} onChange={(e) => setSelected(e.target.value)} style={{padding:'0.5rem', borderRadius:'4px', border:'1px solid #ccc'}}>
          {modifiers.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
        <button onClick={handleRun} disabled={loading || !selected}>
          {loading ? 'Running...' : 'Run'}
        </button>
      </div>
      
      {error && <p className="error-message">{error}</p>}
      
      {result && (
        <div style={{border:'1px solid var(--border-color)', borderRadius:'6px', padding:'1rem'}}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h3 style={{margin:0}}>{result.modifier_name}</h3>
            <Badge category={result.risk_category} />
          </div>
          <p style={{margin:'0.5rem 0'}}><strong>Score:</strong> {result.score}</p>
          <ModifierDetails mod={result} />
        </div>
      )}
    </div>
  );
}
""",
"src/App.jsx": """import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatusCard from './components/StatusCard';
import CompanyForm from './components/CompanyForm';
import RiskSummary from './components/RiskSummary';
import ModifierTable from './components/ModifierTable';
import ReportsList from './components/ReportsList';
import SingleModifierRunner from './components/SingleModifierRunner';
import { checkHealth, analyzeCompany, getReportByFilename } from './api/cyberRiskApi';

function App() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  
  const [currentCompanyData, setCurrentCompanyData] = useState({
    company_name: 'Microsoft',
    domain: 'microsoft.com',
    country: 'USA',
    revenue_band: '> $1B',
    industry: 'Technology'
  });

  useEffect(() => {
    verifyBackend();
  }, []);

  const verifyBackend = async () => {
    try {
      const res = await checkHealth();
      setIsHealthy(res.status === 'healthy');
      setError(null);
    } catch (err) {
      setIsHealthy(false);
    }
  };

  const handleAnalyze = async (formData) => {
    setCurrentCompanyData(formData);
    setLoading(true);
    setError(null);
    setReport(null);
    
    try {
      const data = await analyzeCompany(formData);
      setReport(data);
    } catch (err) {
      setError("Analysis failed. Please check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectReport = async (filename) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getReportByFilename(filename);
      setReport(data);
    } catch (err) {
      setError("Failed to load report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-content">
        <StatusCard isHealthy={isHealthy} />
        
        {error && <div className="error-message">{error}</div>}
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem'}}>
          <CompanyForm onSubmit={handleAnalyze} loading={loading} disabled={!isHealthy} />
          
          <div style={{display:'flex', flexDirection:'column', gap:'2rem'}}>
            <ReportsList onSelectReport={handleSelectReport} />
            <SingleModifierRunner companyData={currentCompanyData} />
          </div>
        </div>

        {report && (
          <div style={{display:'flex', flexDirection:'column', gap:'2rem', animation: 'fadeIn 0.5s ease'}}>
            <RiskSummary report={report} />
            <ModifierTable modifiers={report.modifiers} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
"""
}

def create_frontend():
    update_backend_cors()
    
    os.makedirs(frontend_dir, exist_ok=True)
    
    for relative_path, content in files.items():
        filepath = os.path.join(frontend_dir, relative_path)
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_frontend()
