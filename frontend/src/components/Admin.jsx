import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import JobTitles from './JobTitles.jsx';
import ScrapableDomains from './ScrapableDomains.jsx';
import ScrapeHistory from './ScrapeHistory.jsx';
import api from '../services/api';

const Admin = () => {
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [scheduledTime, setScheduledTime] = useState('');

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await api.get('/scrape-schedule/');
        setScheduledTime(response.data.time);
      } catch (error) {
        console.error('Error fetching scrape schedule:', error);
      }
    };
    fetchSchedule();
  }, []);

  const handleScrape = useCallback(async () => {
    setLoading(true);
    setScrapeStatus('Scraping...');
    try {
      const response = await api.post('/scrape/', { days: 1 });
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

  const handleSaveSchedule = async () => {
    try {
      await api.put('/scrape-schedule/', { time: scheduledTime });
      alert('Schedule saved!');
    } catch (error) {
      console.error('Error saving scrape schedule:', error);
      alert('Error saving schedule.');
    }
  };

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
      <div className="admin-section">
        <h3>Job Management</h3>
        <Link to="/admin/jobs">Jobs Table</Link>
      </div>
      <div>
        <h3>Manual Scrape</h3>
        <button onClick={handleScrape} disabled={loading}>
          {loading ? 'Scraping...' : 'Run Manual 1-Day Scrape'}
        </button>
        {scrapeStatus && <p>{scrapeStatus}</p>}
      </div>
      <div>
        <h3>Scheduled Scrape</h3>
        <label>
          Daily scrape time:
          <input type="time" value={scheduledTime} onChange={(e) => setScheduledTime(e.target.value)} />
        </label>
        <button onClick={handleSaveSchedule}>Save Schedule</button>
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
