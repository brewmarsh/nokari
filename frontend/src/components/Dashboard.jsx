import React from 'react';
import Jobs from './Jobs.jsx';
import './Dashboard.css';

const Dashboard = ({ user }) => {
  console.log('Dashboard render, user:', user);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
      </div>
      <Jobs />
    </div>
  );
};

export default Dashboard;
