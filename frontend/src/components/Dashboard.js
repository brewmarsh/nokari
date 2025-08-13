import React, { useState } from 'react';
import Jobs from './Jobs';
import ScrapableDomains from './ScrapableDomains';
import api from '../services/api';

const Dashboard = () => {
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleScrape = async () => {
    setLoading(true);
    setScrapeStatus('Scraping...');
    try {
      const response = await api.post('/scrape/');
      setScrapeStatus(response.data.detail);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      setScrapeStatus('An error occurred while scraping jobs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={handleScrape} disabled={loading}>
        {loading ? 'Scraping...' : 'Scrape Jobs'}
      </button>
      {scrapeStatus && <p>{scrapeStatus}</p>}
      <Jobs />
      <ScrapableDomains />
    </div>
  );
};

export default Dashboard;
