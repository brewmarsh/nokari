import React, { useState, useCallback } from 'react';
import Jobs from './Jobs.jsx';
import ScrapableDomains from './ScrapableDomains.jsx';
import ScrapeHistory from './ScrapeHistory.jsx';
import JobTitles from './JobTitles.jsx';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = ({ user }) => {
  console.log('Dashboard render, user:', user);
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleScrape = useCallback(async () => {
    setLoading(true);
    setScrapeStatus('Scraping...');
    try {
      const response = await api.post('/scrape/');
      setScrapeStatus(response.data.detail);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        setScrapeStatus(error.response.data.detail);
      } else {
        setScrapeStatus('An error occurred while scraping jobs.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={handleScrape} disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Jobs'}
        </button>
      </div>
      {scrapeStatus && <p>{scrapeStatus}</p>}
      <Jobs />
      {user && user.role === 'admin' && (
        <div className="admin-section">
          <h2>Admin Tools</h2>
          <JobTitles />
          <ScrapableDomains />
          <ScrapeHistory />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
