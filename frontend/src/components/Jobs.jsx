import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './Jobs.css';
import PinIcon from './PinIcon.jsx';
import useDebounce from '../hooks/useDebounce.js';

const ThreeDotsIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
    <path d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>
  </svg>
);

const RemoteIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
  </svg>
);

const Badge = ({ workArrangement }) => {
    const badgeStyle = {
      padding: '4px 8px',
      borderRadius: '12px',
      color: 'white',
      fontSize: '0.8rem',
      fontWeight: 'bold',
      marginLeft: '10px',
      textTransform: 'capitalize',
    };

    const badgeColors = {
      remote: 'var(--secondary-green)',
      hybrid: 'var(--primary-blue)',
      onsite: 'var(--neutral-gray)',
    };

    const style = {
      ...badgeStyle,
      backgroundColor: badgeColors[workArrangement],
    };

    return <span style={style}>{workArrangement}</span>;
  };

const Jobs = () => {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [search, setSearch] = useState('');
  const [openMenu, setOpenMenu] = useState(null);
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);
  const [similarJobsTitle, setSimilarJobsTitle] = useState('');

  const debouncedTitle = useDebounce(title, 500);
  const debouncedCompany = useDebounce(company, 500);
  const debouncedSearch = useDebounce(search, 500);

  const fetchJobs = useCallback(async () => {
    setIsLoadingSimilar(false);
    setSimilarJobsTitle('');
    try {
      const res = await api.get('/jobs/', {
        params: {
          title: debouncedTitle,
          company: debouncedCompany,
          search: debouncedSearch,
        },
      });
      setJobs(res.data);
    } catch (err) {
      setError(err);
    }
  }, [debouncedTitle, debouncedCompany, debouncedSearch]);

  useEffect(() => {
    fetchJobs();
  }, [debouncedTitle, debouncedCompany, debouncedSearch, fetchJobs]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const handleHide = useCallback(async (jobLink) => {
    try {
      await api.post('/jobs/hide/', { job_posting_link: jobLink });
      setJobs(jobs.filter((job) => job.link !== jobLink));
    } catch (err) {
      setError(err);
    }
  }, [jobs]);

  const handleHideCompany = useCallback(async (companyName) => {
    try {
      await api.post('/companies/hide/', { name: companyName });
      setJobs(jobs.filter((job) => job.company !== companyName));
    } catch (err) {
      setError(err);
    }
  }, [jobs]);

  const handlePin = useCallback(async (jobLink, isPinned) => {
    try {
      await api.post('/jobs/pin/', { job_posting_link: jobLink, pinned: !isPinned });
      fetchJobs();
    } catch (err) {
      setError(err);
    }
  }, [fetchJobs]);

  const handleFindSimilar = useCallback(async (job) => {
    setIsLoadingSimilar(true);
    setSimilarJobsTitle(job.title);
    setOpenMenu(null);
    try {
      const res = await api.post(`/jobs/${job.link}/find-similar/`);
      setJobs(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoadingSimilar(false);
    }
  }, []);

  return (
    <div>
      {similarJobsTitle ? (
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          <h1>Jobs similar to "{similarJobsTitle}"</h1>
          <button onClick={fetchJobs} style={{ marginLeft: '20px' }}>Clear</button>
        </div>
      ) : (
        <h1>Job Postings</h1>
      )}
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
      {isLoadingSimilar ? (
        <div>Finding similar jobs...</div>
      ) : (
        <div className="jobs-container">
          {jobs.map((job) => (
            <div key={job.link} className={`job-card ${job.is_pinned ? 'pinned' : ''}`}>
              <button onClick={() => handlePin(job.link, job.is_pinned)} title={job.is_pinned ? 'Unpin Job' : 'Pin Job'} className="pin-icon">
                  <PinIcon isPinned={job.is_pinned} />
              </button>
              <div className="job-card-header">
                <div>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                      <h2 className="job-title"><a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a></h2>
                      <Badge workArrangement={job.work_arrangement} />
                  </div>
                  <p className="company-name">{job.company}</p>
                </div>
                <div className="action-menu">
                  <button onClick={() => setOpenMenu(openMenu === job.link ? null : job.link)} className="three-dots-icon">
                    <ThreeDotsIcon />
                  </button>
                  {openMenu === job.link && (
                    <div className="dropdown-menu">
                      <button onClick={() => { handleHide(job.link); setOpenMenu(null); }}>Hide Job</button>
                      <button onClick={() => handleFindSimilar(job)}>Find similar</button>
                    </div>
                  )}
                </div>
              </div>

              {job.location && (
                  <div className="job-location">
                      <span>{job.location}</span>
                      {job.work_arrangement === 'remote' && <RemoteIcon style={{ color: 'var(--neutral-gray)' }} />}
                      {job.work_arrangement === 'hybrid' && job.days_in_office && (
                          <span style={{ marginLeft: '10px' }}>({job.days_in_office} days in office)</span>
                      )}
                  </div>
              )}

              <p className="description">{job.description}</p>
              <p className="posting-date">
                {new Date(job.posting_date).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Jobs;
