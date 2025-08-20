import React, { useState, useCallback } from 'react';
import JobTitles from './JobTitles.jsx';
import ScrapableDomains from './ScrapableDomains.jsx';
import ScrapeHistory from './ScrapeHistory.jsx';
import api from '../services/api';

const Admin = () => {
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(7); // Default to 7 days
  const [users, setUsers] = useState([]);

  const handleScrape = useCallback(async () => {
    setLoading(true);
    setScrapeStatus('Scraping...');
    try {
      const response = await api.post('/scrape/', { days });
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
  }, [days]);

  const fetchUsers = useCallback(async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }, []);

  const promoteUser = useCallback(async (userId) => {
    try {
      await api.post(`/users/${userId}/promote/`);
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error promoting user:', error);
    }
  }, [fetchUsers]);

  React.useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <div className="admin-section">
      <h2>Admin Tools</h2>
      <div>
        <h3>Scrape Jobs</h3>
        <label>
          Scrape jobs from the last (days):
          <input type="number" value={days} onChange={(e) => setDays(e.target.value)} />
        </label>
        <button onClick={handleScrape} disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Jobs'}
        </button>
        {scrapeStatus && <p>{scrapeStatus}</p>}
      </div>
      <JobTitles />
      <ScrapableDomains />
      <ScrapeHistory />
      <div>
        <h3>Users</h3>
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  {user.role !== 'admin' && (
                    <button onClick={() => promoteUser(user.id)}>Promote to Admin</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Admin;
