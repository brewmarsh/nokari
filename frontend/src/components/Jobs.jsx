import React, { useState, useEffect, useCallback } from 'react';
import './Jobs.css';
import useDebounce from '../hooks/useDebounce.js';
import { auth } from '../firebaseConfig';
import api from '../services/api';

import JobCard from './JobCard.jsx';
import JobFilters from './JobFilters.jsx';

const JOBS_PER_PAGE = 20;

const Jobs = ({ preferences, user }) => {
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

  const [lastDocId, setLastDocId] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [resetKey, setResetKey] = useState(0);

  useEffect(() => {
    localStorage.setItem('filtersVisible', JSON.stringify(filtersVisible));
  }, [filtersVisible]);

  const debouncedTitle = useDebounce(title, 500);
  const debouncedCompany = useDebounce(company, 500);

  const fetchJobs = useCallback(async (isLoadMore = false) => {
     if (loading) return;
     setLoading(true);
     setError(null);

     try {
         const params = {
             limit: JOBS_PER_PAGE,
             last_doc_id: isLoadMore ? lastDocId : undefined,
         };

         if (debouncedTitle) params.title = debouncedTitle;
         if (debouncedCompany) params.company = debouncedCompany;
         if (preferences && preferences.length > 0) params.locations = preferences;

         const response = await api.get('/jobs', { params });
         const fetchedJobs = response.data;

         if (isLoadMore) {
             setJobs(prevJobs => [...prevJobs, ...fetchedJobs]);
         } else {
             setJobs(fetchedJobs);
         }

         if (fetchedJobs.length > 0) {
             setLastDocId(fetchedJobs[fetchedJobs.length - 1].job_id);
         } else if (!isLoadMore) {
             setLastDocId(null);
         }

         if (fetchedJobs.length < JOBS_PER_PAGE) {
             setHasMore(false);
         } else {
             setHasMore(true);
         }
     } catch (err) {
         console.error("Error fetching jobs:", err);
         setError(err);
     } finally {
         setLoading(false);
     }
  }, [debouncedTitle, debouncedCompany, preferences, lastDocId, loading]);


  // Effect for initial load and filter changes
  useEffect(() => {
    // Reset state and fetch
    setJobs([]);
    setLastDocId(null);
    setHasMore(true);

    const initialFetch = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = {
                 limit: JOBS_PER_PAGE,
            };

            if (debouncedTitle) params.title = debouncedTitle;
            if (debouncedCompany) params.company = debouncedCompany;
            if (preferences && preferences.length > 0) params.locations = preferences;

            const response = await api.get('/jobs', { params });
            const fetchedJobs = response.data;

            setJobs(fetchedJobs);

            if (fetchedJobs.length > 0) {
                setLastDocId(fetchedJobs[fetchedJobs.length - 1].job_id);
            }

            if (fetchedJobs.length < JOBS_PER_PAGE) {
                setHasMore(false);
            } else {
                setHasMore(true);
            }
        } catch(err) {
             console.error("Error fetching jobs:", err);
             setError(err);
        } finally {
            setLoading(false);
        }
    };

    initialFetch();
  }, [debouncedTitle, debouncedCompany, preferences, resetKey]);

  const handleLoadMore = () => {
    fetchJobs(true);
  };

  const handleClearSimilar = () => {
      setSimilarJobsTitle('');
      setResetKey(prev => prev + 1);
  };

  const handleHide = useCallback(async (jobId) => {
    const user = auth.currentUser;
    if (!user) return;

    try {
      await api.post(`/jobs/${jobId}/hide`);
      setJobs(jobs.filter((job) => job.job_id !== jobId));
    } catch (err) {
      console.error("Error hiding job:", err);
      setError(err);
    }
  }, [jobs]);

  const handleHideCompany = useCallback(async (companyName) => {
    const user = auth.currentUser;
    if (!user) return;

    try {
      await api.post(`/companies/${companyName}/hide`);
      setJobs(jobs.filter((job) => job.company !== companyName));
    } catch (err) {
      console.error("Error hiding company:", err);
      setError(err);
    }
  }, [jobs]);

  const handlePin = useCallback(async (jobId, isPinned) => {
    const user = auth.currentUser;
    if (!user) return;

    try {
      await api.post(`/jobs/${jobId}/pin`, null, { params: { is_pinned: !isPinned } });
      setJobs(prevJobs => prevJobs.map(job =>
          job.job_id === jobId ? { ...job, is_pinned: !isPinned } : job
      ));
    } catch (err) {
      console.error("Error pinning job:", err);
      setError(err);
    }
  }, []);

  const handleFindSimilar = useCallback(async (job) => {
    setIsLoadingSimilar(true);
    setSimilarJobsTitle(job.title);
    setOpenMenu(null);
    try {
      await api.post(`/jobs/${job.job_id}/find-similar`);
       alert("Similarity search initiated. Check back later.");
    } catch (err) {
      console.error("Error finding similar jobs:", err);
      setError(err);
    } finally {
      setIsLoadingSimilar(false);
    }
  }, []);

  const handleBlockUrl = useCallback(async (pattern) => {
    try {
      await api.post("/admin/blocked-patterns/", { pattern });
      alert(`Blocked pattern: ${pattern}`);
    } catch (err) {
      console.error("Error blocking pattern:", err);
      alert(`Error blocking pattern: ${err.message}`);
    }
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      {similarJobsTitle ? (
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          <h1>Jobs similar to "{similarJobsTitle}"</h1>
          <button onClick={handleClearSimilar} style={{ marginLeft: '20px' }}>Clear</button>
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
                key={job.job_id} // Use job_id from API
                job={job}
                openMenu={openMenu}
                setOpenMenu={setOpenMenu}
                handlePin={handlePin}
                handleHide={handleHide}
                handleHideCompany={handleHideCompany}
                handleFindSimilar={handleFindSimilar}
                isAdmin={user?.role?.toLowerCase() === 'admin'}
                handleBlockUrl={handleBlockUrl}
              />
            ))}
          </div>
          {hasMore && (
              <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
                  <button onClick={handleLoadMore} disabled={loading}>
                      {loading ? 'Loading...' : 'Load More'}
                  </button>
              </div>
          )}
        </>
      )}
    </div>
  );
};

export default Jobs;
