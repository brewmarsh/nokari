import React, { useState, useEffect } from 'react';
import api from '../services/api';

const ScrapableDomains = () => {
  const [domains, setDomains] = useState([]);
  const [error, setError] = useState(null);
  const [domain, setDomain] = useState('');

  const fetchDomains = async () => {
    try {
      const res = await api.get('/scrapable-domains/');
      setDomains(res.data);
    } catch (err) {
      setError(err);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  const onChange = (e) => setDomain(e.target.value);

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/scrapable-domains/', { domain });
      setDomain('');
      fetchDomains();
    } catch (err) {
      setError(err);
    }
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>Scrapable Domains</h1>
      <form onSubmit={onSubmit}>
        <input
          type="text"
          placeholder="Enter a domain"
          value={domain}
          onChange={onChange}
          required
        />
        <button type="submit">Add Domain</button>
      </form>
      <ul>
        {domains.map((d) => (
          <li key={d.id}>{d.domain}</li>
        ))}
      </ul>
    </div>
  );
};

export default ScrapableDomains;
