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

      <div style={{background:'#f8fafc', padding:'1.5rem', borderRadius:'8px', marginBottom:'2rem', border:'1px solid var(--border-color)'}}>
        <h3 style={{margin:'0 0 0.5rem 0', fontSize:'1.1rem', color:'var(--text-main)'}}>Modifier Guidelines</h3>
        <p style={{margin:'0 0 1rem 0', fontSize:'0.95rem', color:'var(--text-muted)'}}>{mod.description}</p>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem'}}>
          <div>
            <strong style={{color:'var(--text-main)', fontSize:'0.9rem'}}>Target Parameter:</strong>
            <div style={{fontSize:'0.9rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>{mod.target_parameter || 'N/A'}</div>
          </div>
          <div>
            <strong style={{color:'var(--text-main)', fontSize:'0.9rem'}}>Research Needed:</strong>
            <div style={{fontSize:'0.9rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>{mod.research_needed || 'N/A'}</div>
          </div>
        </div>
      </div>

      {mod.reason_for_score && (
        <div style={{marginBottom: '2rem'}}>
          <h3 style={{color:'var(--text-muted)', borderBottom:'1px solid var(--border-color)', paddingBottom:'0.5rem', marginTop: 0}}>Scoring Reason</h3>
          <p style={{fontSize:'1.05rem', lineHeight:1.6, margin: '0.5rem 0 0 0', fontWeight: 500, color: 'var(--text-main)'}}>
            {mod.reason_for_score}
          </p>
        </div>
      )}

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
