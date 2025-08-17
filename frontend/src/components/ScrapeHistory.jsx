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
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>User</th>
            <th>Status</th>
            <th>Jobs Found</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td>{new Date(item.timestamp).toLocaleString()}</td>
              <td>{item.user}</td>
              <td>{item.status}</td>
              <td>{item.jobs_found}</td>
              <td>{item.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScrapeHistory;
