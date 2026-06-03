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

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const isValidDomain = (d) => {
    let domainStr = d.replace(/^https?:\/\//, '').replace(/\/$/, '');
    if (domainStr.includes('@') || domainStr.includes(' ')) return false;
    if (!domainStr.includes('.')) return false;
    if (domainStr.includes('..')) return false;
    const domainRegex = /^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return domainRegex.test(domainStr);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.company_name || !formData.domain || !formData.country) {
      setError('Company Name, Domain, and Country are required.');
      return;
    }
    if (!isValidDomain(formData.domain)) {
      setError('Please enter a valid company domain, for example microsoft.com.');
      return;
    }
    setError('');
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2>Analyze Company</h2>
      
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
