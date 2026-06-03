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
