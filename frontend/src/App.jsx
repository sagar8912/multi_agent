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
      const errorMsg = err.response?.data?.detail || err.message || 'Something went wrong generating report';
      addToast(errorMsg, 'error');
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
                    <th>Status</th>
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
                      <td>
                        <span style={{
                          padding:'0.2rem 0.5rem', borderRadius:'4px', fontSize:'0.75rem', fontWeight:600,
                          background: mod.status === 'active' ? '#dbeafe' : mod.status === 'partial_mvp' ? '#fef3c7' : '#f1f5f9',
                          color: mod.status === 'active' ? '#1e40af' : mod.status === 'partial_mvp' ? '#92400e' : '#475569'
                        }}>
                          {mod.status === 'not_implemented_phase_2' ? 'PHASE 2' : mod.status === 'partial_mvp' ? 'PARTIAL MVP' : 'ACTIVE'}
                        </span>
                      </td>
                      <td><span style={{fontWeight:800, fontSize:'1.1rem'}}>{mod.status === 'not_implemented_phase_2' ? '-' : mod.score}</span></td>
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
                          {mod.verification_status?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
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
              <div style={{marginTop: '1rem', fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic'}}>
                * This MVP currently automates public web evidence collection for selected modifiers. Some modifiers require paid data sources, SEC filings, D&B, or business-validated rules.
              </div>
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
