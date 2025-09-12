import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './Jobs.css';
import useDebounce from '../hooks/useDebounce.js';

import JobCard from './JobCard.jsx';
import JobFilters from './JobFilters.jsx';

const Jobs = ({ preferences }) => {
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
          work_arrangement: preferences.join(','),
        },
      });
      setJobs(res.data);
    } catch (err) {
      setError(err);
    }
  }, [debouncedTitle, debouncedCompany, debouncedSearch, preferences]);

  useEffect(() => {
    fetchJobs();
  }, [debouncedTitle, debouncedCompany, debouncedSearch, fetchJobs, preferences]);

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
      <JobFilters
        filtersVisible={filtersVisible}
        setFiltersVisible={setFiltersVisible}
        title={title}
        setTitle={setTitle}
        company={company}
        setCompany={setCompany}
        search={search}
        setSearch={setSearch}
      />
      {isLoadingSimilar ? (
        <div>Finding similar jobs...</div>
      ) : (
        <>
          {similarJobsTitle && jobs.length === 0 && !isLoadingSimilar && (
            <div style={{ marginTop: '20px' }}>No similar jobs found.</div>
          )}
          <div className="jobs-container">
            {jobs.map((job) => (
              <JobCard
                key={job.link}
                job={job}
                openMenu={openMenu}
                setOpenMenu={setOpenMenu}
                handlePin={handlePin}
                handleHide={handleHide}
                handleHideCompany={handleHideCompany}
                handleFindSimilar={handleFindSimilar}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Jobs;
