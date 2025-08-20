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

const HideIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
        <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.94 5.94 0 0 1 8 4.5a5.94 5.94 0 0 1 4.5 2.066 6.872 6.872 0 0 1 1.482 1.943l.359.492zM10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
        <path d="M12.454 14.394l-1.09-1.09a3.504 3.504 0 0 0-4.34-4.34L6.11 8.047a4.5 4.5 0 0 0-1.79 3.183l-1.65-1.65A9.24 9.24 0 0 0 0 8a12.17 12.17 0 0 0 3.546 4.359l.87.87L.707 15.293a1 1 0 0 0 1.414 1.414l12-12a1 1 0 0 0-1.414-1.414L12.454 14.394zM16 8c-.011.02-.022.04-.033.06L1.64 1.64C1.33 2.083 1 2.518 1 3.27a11.17 11.17 0 0 0 2.223 4.298l.64.639a5.5 5.5 0 0 0 7.583 1.25l.822.822A9.23 9.23 0 0 1 8 13.5a9.23 9.23 0 0 1-4.25-1.108l.63.628A11.17 11.17 0 0 0 8 15.5c5 0 8-5.5 8-5.5s-.288-.521-.641-1.06z"/>
    </svg>
);

const Badge = ({ location }) => {
    const badgeStyle = {
      padding: '4px 8px',
      borderRadius: '12px',
      color: 'white',
      fontSize: '0.8rem',
      fontWeight: 'bold',
      marginRight: '5px',
      textTransform: 'capitalize',
    };

    const badgeColors = {
      remote: 'var(--secondary-green)',
      hybrid: 'var(--primary-blue)',
      onsite: 'var(--neutral-gray)',
    };

    const style = {
      ...badgeStyle,
      backgroundColor: badgeColors[location.type],
    };

    return <span style={style}>{location.type}</span>;
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
  const [filtersVisible, setFiltersVisible] = useState(true);

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
      <button onClick={() => setFiltersVisible(!filtersVisible)}>
        {filtersVisible ? 'Hide Filters' : 'Show Filters'}
      </button>
      {filtersVisible && (
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
      )}
      {isLoadingSimilar ? (
        <div>Finding similar jobs...</div>
      ) : (
        <>
          {similarJobsTitle && jobs.length === 0 && !isLoadingSimilar && (
            <div style={{ marginTop: '20px' }}>No similar jobs found.</div>
          )}
          <div className="jobs-container">
            {jobs.map((job) => (
              <div key={job.link} className={`job-card ${job.is_pinned ? 'pinned' : ''}`}>
                <div className="job-card-header">
                <button onClick={() => handlePin(job.link, job.is_pinned)} title={job.is_pinned ? 'Unpin Job' : 'Pin Job'} className="pin-icon">
                    <PinIcon isPinned={job.is_pinned} />
                </button>
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

              <h2 className="job-title"><a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a></h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <p className="company-name">{job.company}</p>
                <button onClick={() => handleHideCompany(job.company)} style={{ background: 'none', border: 'none', color: 'var(--neutral-gray)', cursor: 'pointer' }} title="Hide Company">
                    <HideIcon />
                </button>
              </div>

              {job.locations && job.locations.length > 0 && (
                <div className="job-location">
                  {job.locations.map((loc, index) => (
                    <div key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                      <Badge location={loc} />
                      {loc.location_string && <span>{loc.location_string}</span>}
                    </div>
                  ))}
                  {job.days_in_office && (
                    <span style={{ marginLeft: '10px' }}>({job.days_in_office} days in office)</span>
                  )}
                </div>
              )}

              <p className="description">{job.description}</p>
              <p className="posting-date">
                Posted on: {new Date(job.posting_date).toLocaleDateString()}
              </p>
            </div>
          ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Jobs;
