import React from 'react';
import Jobs from './Jobs';
import ScrapableDomains from './ScrapableDomains';
import api from '../services/api';

const Dashboard = () => {
  const handleScrape = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('You must be logged in to scrape jobs.');
        return;
      }
      const response = await api.post('/scrape/', {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      alert(response.data.detail);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      alert('An error occurred while scraping jobs.');
    }
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={handleScrape}>Scrape Jobs</button>
      <Jobs />
      <ScrapableDomains />
    </div>
  );
};

export default Dashboard;
