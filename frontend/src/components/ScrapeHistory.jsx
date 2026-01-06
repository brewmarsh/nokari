import React, { useState, useEffect } from 'react';
import api from '../services/api';

const ScrapeHistory = () => {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/scrape-history/');
        setHistory(res.data);
      } catch (err) {
        setError(err);
      }
    };
    fetchHistory();
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>Scrape History</h1>
      <table style={{ width: '100%', textAlign: 'center' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'center' }}>Timestamp</th>
            <th style={{ textAlign: 'center' }}>User</th>
            <th style={{ textAlign: 'center' }}>Status</th>
            <th style={{ textAlign: 'center' }}>Jobs Found</th>
            <th style={{ textAlign: 'center' }}>Details</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td style={{ textAlign: 'center' }}>{new Date(item.timestamp).toLocaleString()}</td>
              <td style={{ textAlign: 'center' }}>{item.requested_by || 'System'}</td>
              <td style={{ textAlign: 'center' }}>{item.status}</td>
              <td style={{ textAlign: 'center' }}>{item.jobs_found}</td>
              <td style={{ textAlign: 'center' }}>{item.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScrapeHistory;
