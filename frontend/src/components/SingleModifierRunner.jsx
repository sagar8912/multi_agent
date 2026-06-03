import React, { useState, useEffect } from 'react';
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
