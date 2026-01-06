import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import JobTitles from './JobTitles.jsx';
import ScrapableDomains from './ScrapableDomains.jsx';
import ScrapeHistory from './ScrapeHistory.jsx';
import BlockedPatterns from './BlockedPatterns.jsx';
import AdminOverview from './AdminOverview.jsx';
import AdminUsers from './AdminUsers.jsx';
import './AdminLayout.css';

const Admin = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <AdminOverview />;
      case 'job-titles':
        return (
            <div>
                <h3>Job Titles Configuration</h3>
                <JobTitles />
            </div>
        );
      case 'domains':
        return (
            <div>
                <h3>Scrapable Domains Configuration</h3>
                <ScrapableDomains />
            </div>
        );
      case 'blocked-patterns':
        return (
            <div>
                <h3>Blocked Patterns Configuration</h3>
                <BlockedPatterns />
            </div>
        );
      case 'history':
        return (
            <div>
                <h3>Scrape History Log</h3>
                <ScrapeHistory />
            </div>
        );
      case 'users':
        return <AdminUsers />;
      default:
        return <AdminOverview />;
    }
  };

  return (
    <div className="admin-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2>Admin Dashboard</h2>
        <Link to="/admin/jobs" className="button" style={{
            backgroundColor: 'var(--primary)',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius)',
            fontSize: '0.95rem',
            display: 'inline-block'
        }}>
            Manage Jobs Table
        </Link>
      </div>

      <div className="admin-container">
        <div className="admin-sidebar">
          <div className="admin-sidebar-header">Main Menu</div>

          <div
            className={`admin-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </div>

          <div className="admin-sidebar-header" style={{ marginTop: '1rem' }}>Configuration</div>

          <div
            className={`admin-nav-item ${activeTab === 'job-titles' ? 'active' : ''}`}
            onClick={() => setActiveTab('job-titles')}
          >
            Job Titles
          </div>

          <div
            className={`admin-nav-item ${activeTab === 'domains' ? 'active' : ''}`}
            onClick={() => setActiveTab('domains')}
          >
            Scrapable Domains
          </div>

          <div
            className={`admin-nav-item ${activeTab === 'blocked-patterns' ? 'active' : ''}`}
            onClick={() => setActiveTab('blocked-patterns')}
          >
            Blocked Patterns
          </div>

          <div className="admin-sidebar-header" style={{ marginTop: '1rem' }}>System</div>

          <div
            className={`admin-nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Scrape History
          </div>

          <div
            className={`admin-nav-item ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </div>
        </div>

        <div className="admin-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Admin;
