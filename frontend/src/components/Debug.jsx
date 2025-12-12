import React from 'react';
import { firebaseConfig, initializationError, auth } from '../firebaseConfig';

const Debug = () => {
  const configKeys = [
    'apiKey',
    'authDomain',
    'projectId',
    'storageBucket',
    'messagingSenderId',
    'appId',
    'measurementId'
  ];

  const safeConfig = {};
  configKeys.forEach(key => {
    const val = firebaseConfig[key];
    if (!val) {
      safeConfig[key] = 'MISSING/EMPTY';
    } else if (val === 'undefined') {
      safeConfig[key] = '"undefined" (string)';
    } else if (val === 'null') {
        safeConfig[key] = '"null" (string)';
    } else {
      // Mask values for safety, but show first/last chars to verify
      if (val.length > 8) {
        safeConfig[key] = `${val.substring(0, 4)}...${val.substring(val.length - 4)}`;
      } else {
        safeConfig[key] = val; // Short values shown as is
      }
    }
  });

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Debug Information</h1>

      <section style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h2>Firebase Configuration Status</h2>
        {initializationError ? (
          <div style={{ color: 'red', fontWeight: 'bold' }}>
            <h3>Initialization Error:</h3>
            <p>{initializationError.message}</p>
          </div>
        ) : (
          <div style={{ color: 'green', fontWeight: 'bold' }}>
             Initialization Successful
          </div>
        )}
      </section>

      <section style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h2>Configuration Values (Masked)</h2>
        <p>Verify that these match your Firebase Console settings.</p>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', backgroundColor: '#f5f5f5' }}>
              <th style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>Key</th>
              <th style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>Value</th>
              <th style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {configKeys.map(key => {
                const isSuspicious = safeConfig[key] === 'MISSING/EMPTY' || safeConfig[key].includes('"undefined"');
                return (
                    <tr key={key}>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>{key}</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd', fontFamily: 'monospace' }}>{safeConfig[key]}</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd', color: isSuspicious ? 'red' : 'green' }}>
                        {isSuspicious ? 'Check Config!' : 'OK'}
                    </td>
                    </tr>
                );
            })}
          </tbody>
        </table>
      </section>

      <section style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h2>Environment</h2>
        <p><strong>App Version:</strong> {process.env.APP_VERSION || 'Unknown'}</p>
        <p><strong>Auth Initialized:</strong> {auth ? 'Yes' : 'No'}</p>
        <p><strong>Current Domain:</strong> {window.location.hostname}</p>
        <p><strong>User Agent:</strong> {navigator.userAgent}</p>
      </section>

      <div style={{ marginTop: '20px' }}>
          <a href="/login" style={{ marginRight: '15px' }}>Back to Login</a>
          <a href="/dashboard">Back to Dashboard</a>
      </div>
    </div>
  );
};

export default Debug;
