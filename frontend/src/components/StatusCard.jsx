import React from 'react';

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
