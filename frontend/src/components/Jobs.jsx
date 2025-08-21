import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './Jobs.css';
import PinIcon from './PinIcon.jsx';
import useDebounce from '../hooks/useDebounce.js';
import ThreeDotsIcon from './icons/ThreeDotsIcon.jsx';
import RemoteIcon from './icons/RemoteIcon.jsx';
import HideIcon from './icons/HideIcon.jsx';

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
  const [filtersVisible, setFiltersVisible] = useState(() => {
    const saved = localStorage.getItem('filtersVisible');
    return saved !== null ? JSON.parse(saved) : true;
  });

  useEffect(() => {
    localStorage.setItem('filtersVisible', JSON.stringify(filtersVisible));
  }, [filtersVisible]);

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
      const res = await api.post('/jobs/find-similar/', { link: job.link });
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
                <div className="job-card-main">
                  <div className="job-card-header">
                    <h2 className="job-title">
                      <a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a>
                    </h2>
                    <div className="action-menu">
                      <button onClick={() => handlePin(job.link, job.is_pinned)} title={job.is_pinned ? 'Unpin Job' : 'Pin Job'} className="pin-icon">
                        <PinIcon isPinned={job.is_pinned} />
                      </button>
                      <button onClick={() => setOpenMenu(openMenu === job.link ? null : job.link)} className="three-dots-icon">
                        <ThreeDotsIcon />
                      </button>
                      {openMenu === job.link && (
                        <div className="dropdown-menu">
                          <button onClick={() => { handleHide(job.link); setOpenMenu(null); }}>Hide Job</button>
                          <button onClick={() => { handleHideCompany(job.company); setOpenMenu(null); }}>Hide Company</button>
                          <button onClick={() => handleFindSimilar(job)}>Find similar</button>
                        </div>
                      )}
                    </div>
                  </div>
                  <p className="company-name">{job.company}</p>
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
                </div>
                <div className="job-card-footer">
                  <p className="posting-date">
                    Posted on: {new Date(job.posting_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
          ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Jobs;
