import React from 'react';
import Jobs from './Jobs';
import ScrapableDomains from './ScrapableDomains';

const Dashboard = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <Jobs />
      <ScrapableDomains />
    </div>
  );
};

export default Dashboard;
