import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Jobs.css';
import PinIcon from './PinIcon';
import HideIcon from './HideIcon';

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

  const handleHide = async (jobLink) => {
    try {
      await api.post('/jobs/hide/', { job_posting_link: jobLink });
      setJobs(jobs.filter((job) => job.link !== jobLink));
    } catch (err) {
      setError(err);
    }
  };

  const handleHideCompany = async (companyName) => {
    try {
      await api.post('/companies/hide/', { name: companyName });
      setJobs(jobs.filter((job) => job.company !== companyName));
    } catch (err) {
      setError(err);
    }
  };

  const handlePin = async (jobLink, isPinned) => {
    try {
      await api.post('/jobs/pin/', { job_posting_link: jobLink, pinned: !isPinned });
      fetchJobs();
    } catch (err) {
      setError(err);
    }
  };

  const handleFindRelated = (jobTitle) => {
    setTitle(jobTitle);
  };

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
      <div className="jobs-container">
        {jobs.map((job) => (
          <div key={job.link} className={`job-card ${job.is_pinned ? 'pinned' : ''}`}>
            <div className="job-card-header">
              <h2 className="job-title"><a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a></h2>
              <div className="job-card-icons">
                <button onClick={() => handlePin(job.link, job.is_pinned)} title={job.is_pinned ? 'Unpin Job' : 'Pin Job'} className="pin-icon"><PinIcon /></button>
                <button onClick={() => handleHide(job.link)} title="Hide Job" className="hide-icon"><HideIcon /></button>
              </div>
            </div>
            <p className="company-name">
              {job.company}
              <button onClick={() => handleHideCompany(job.company)}>Hide Company</button>
            </p>
            <p className="description">{job.description}</p>
            <p className="posting-date">
              {new Date(job.posting_date).toLocaleDateString()}
            </p>
            <button onClick={() => handleFindRelated(job.title)}>Find Related</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Jobs;
