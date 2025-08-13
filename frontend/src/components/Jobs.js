import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Jobs = () => {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [search, setSearch] = useState('');

  const fetchJobs = async () => {
    try {
      const res = await api.get('/jobs/', {
        params: {
          title,
          company,
          search,
        },
      });
      setJobs(res.data);
    } catch (err) {
      setError(err);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [title, company, search]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>Job Postings</h1>
      <div>
        <input
          type="text"
          placeholder="Filter by title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          type="text"
          placeholder="Filter by company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        />
        <input
          type="text"
          placeholder="Search by keyword"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {jobs.map((job) => (
        <div key={job.link}>
          <h2><a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a></h2>
          <p>{job.company}</p>
          <p>{job.description}</p>
        </div>
      ))}
    </div>
  );
};

export default Jobs;
