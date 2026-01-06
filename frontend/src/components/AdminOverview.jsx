import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AdminOverview = () => {
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [scheduledTime, setScheduledTime] = useState('');
  const [flexMinutes, setFlexMinutes] = useState(0);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await api.get('/scrape-schedule/');
        setScheduledTime(response.data.time);
        setFlexMinutes(response.data.flex_minutes || 0);
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
      await api.put('/scrape-schedule/', { time: scheduledTime, flex_minutes: parseInt(flexMinutes, 10) });
      alert('Schedule saved!');
    } catch (error) {
      console.error('Error saving scrape schedule:', error);
      alert('Error saving schedule.');
    }
  };

  return (
    <div className="admin-overview">
      <h3>System Overview & Controls</h3>

      <div className="card" style={{ marginBottom: '20px' }}>
        <h4>Manual Scrape</h4>
        <p className="text-muted">Trigger a manual scrape for the last 24 hours.</p>
        <button onClick={handleScrape} disabled={loading}>
          {loading ? 'Scraping...' : 'Run Manual 1-Day Scrape'}
        </button>
        {scrapeStatus && <p style={{ marginTop: '10px', fontWeight: 'bold' }}>{scrapeStatus}</p>}
      </div>

      <div className="card">
        <h4>Scheduled Scrape</h4>
        <p className="text-muted">Configure when the daily automated scrape runs.</p>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
              Daily Time (UTC)
            </label>
            <input
              type="time"
              value={scheduledTime}
              onChange={(e) => setScheduledTime(e.target.value)}
              style={{ width: '150px', marginBottom: 0 }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
              Flex (minutes)
            </label>
            <input
              type="number"
              value={flexMinutes}
              onChange={(e) => setFlexMinutes(e.target.value)}
              style={{ width: '100px', marginBottom: 0 }}
            />
          </div>
          <button onClick={handleSaveSchedule}>Save Schedule</button>
        </div>
      </div>
    </div>
  );
};

export default AdminOverview;
