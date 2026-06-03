import React, { useState } from 'react';
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
