import React from 'react';
import { downloadJsonUrl, downloadPdfUrl } from '../api/cyberRiskApi';

export const getBadgeColor = (category) => {
  switch(category) {
    case 'Very Favorable': return 'var(--risk-very-fav)';
    case 'Favorable': return 'var(--risk-fav)';
    case 'Average': return 'var(--risk-avg)';
    case 'Partially Unfavorable': return 'var(--risk-part-unfav)';
    case 'Unfavorable': return 'var(--risk-unfav)';
    case 'Manual Review Required': return '#475569'; // slate-600
    case 'Unknown': return 'var(--risk-unknown)';
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
  
  const genTime = report.generated_at_local || (report.generated_at ? new Date(report.generated_at).toLocaleString() : 'Unknown');

  return (
    <div>
      <div className="card" style={{marginBottom: '2rem'}}>
        <h2 style={{borderBottom:'none', margin:0, marginBottom:'1rem'}}>Company Details</h2>
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(250px, 1fr))', gap:'1.5rem', fontSize:'0.95rem'}}>
          <div><strong style={{color:'var(--text-muted)'}}>Company</strong><br/><span style={{fontSize:'1.1rem', fontWeight:600}}>{report.company_name}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Input Domain</strong><br/><span style={{fontSize:'1.1rem'}}>{report.domain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Normalized Domain</strong><br/><span style={{fontSize:'1.1rem', color:'var(--accent-blue)', fontWeight:600}}>{normalizedDomain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Country</strong><br/><span style={{fontSize:'1.1rem'}}>{report.country}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Revenue Band</strong><br/><span style={{fontSize:'1.1rem'}}>{report.revenue_band}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Industry</strong><br/><span style={{fontSize:'1.1rem'}}>{report.industry || 'N/A'}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Report Generated At</strong><br/><span>{genTime}</span></div>
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
        
        {report.manual_review_required && (
          <div style={{background: '#fef2f2', border: '1px solid #f87171', color: '#b91c1c', padding: '1rem', borderRadius: '8px', marginTop: '1rem', fontWeight: 600}}>
            ⚠️ Manual underwriting review is required because evidence is insufficient or the website appears non-business/generic.
          </div>
        )}
        {!report.manual_review_required && report.overall_confidence < 0.25 && (
            <div style={{background: '#fffbeb', border: '1px solid #fde68a', color: '#b45309', padding: '1rem', borderRadius: '8px', marginTop: '1rem', fontWeight: 600}}>
                ⚠️ Low confidence result. Manual validation is recommended.
            </div>
        )}

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
          
          <div className="summary-stat" style={{backgroundColor: getBadgeColor(report.overall_risk_category), color:'white', border:'none', display:'flex', flexDirection:'column', justifyContent:'center'}}>
            <span style={{fontSize:'0.9rem', opacity:0.9, textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Risk Category</span>
            <div style={{fontSize: report.overall_risk_category === 'Manual Review Required' ? '1.5rem' : '2.2rem', fontWeight:'800', marginTop:'0.5rem', lineHeight:1.2, textAlign: 'center'}}>{report.overall_risk_category}</div>
          </div>

          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Confidence</span>
            <div style={{fontSize:'3rem', fontWeight:'800', color: 'var(--text-main)'}}>{(report.overall_confidence * 100).toFixed(0)}%</div>
          </div>

          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Evidence Quality</span>
            <div style={{fontSize:'2.5rem', fontWeight:'800', color: report.evidence_quality === 'High' ? '#16a34a' : report.evidence_quality === 'Medium' ? '#d97706' : '#dc2626'}}>{report.evidence_quality || 'N/A'}</div>
            <div style={{marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)'}}>
              Manual Review: {report.manual_review_required ? <strong style={{color: '#dc2626'}}>Yes</strong> : <strong>No</strong>}
            </div>
          </div>
          
          <div className="summary-stat" style={{gridColumn: '1 / -1', textAlign:'left', padding:'2rem'}}>
            <h3 style={{margin:'0 0 1rem 0', fontSize:'1.2rem', color:'var(--text-main)'}}>Underwriter Summary</h3>
            <p style={{margin:0, whiteSpace:'pre-wrap', lineHeight:1.6, color:'var(--text-main)', fontSize:'1.05rem'}}>{report.underwriter_summary}</p>
            
            <div style={{marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '2rem'}}>
              <div style={{flex: 1}}>
                <h4 style={{margin: '0 0 0.75rem 0', color: '#16a34a'}}>Key Favorable Drivers</h4>
                <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                  {report.top_positive_drivers && report.top_positive_drivers.length > 0 ? (
                    report.top_positive_drivers.map(driver => (
                      <span key={driver} style={{background: '#dcfce7', color: '#166534', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600}}>{driver}</span>
                    ))
                  ) : (
                    <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>None identified</span>
                  )}
                </div>
              </div>
              <div style={{flex: 1}}>
                <h4 style={{margin: '0 0 0.75rem 0', color: '#dc2626'}}>Key Risk Drivers</h4>
                <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                  {report.top_negative_drivers && report.top_negative_drivers.length > 0 ? (
                    report.top_negative_drivers.map(driver => (
                      <span key={driver} style={{background: '#fee2e2', color: '#991b1b', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600}}>{driver}</span>
                    ))
                  ) : (
                    <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>None identified</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
