import React, { useState, useEffect, useCallback } from 'react';
import './Jobs.css';
import useDebounce from '../hooks/useDebounce.js';
import { db, auth } from '../firebaseConfig';
import { collection, query, where, getDocs, doc, setDoc, orderBy, limit, startAfter } from 'firebase/firestore';
import api from '../services/api'; // Keep api for find-similar for now

import JobCard from './JobCard.jsx';
import JobFilters from './JobFilters.jsx';

const JOBS_PER_PAGE = 20;

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

  const [lastDoc, setLastDoc] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [resetKey, setResetKey] = useState(0); // Add a key to force re-fetch

  useEffect(() => {
    localStorage.setItem('filtersVisible', JSON.stringify(filtersVisible));
  }, [filtersVisible]);

  const debouncedTitle = useDebounce(title, 500);
  const debouncedCompany = useDebounce(company, 500);

  // Common function to build the query
  const buildQuery = useCallback((startAfterDoc = null) => {
    const jobsRef = collection(db, "job_postings");
    let q = query(jobsRef);

    if (debouncedTitle) {
      q = query(q, where("title", "==", debouncedTitle));
    }
    if (debouncedCompany) {
      q = query(q, where("company", "==", debouncedCompany));
    }
    if (preferences && preferences.length > 0) {
      q = query(q, where("locations", "array-contains-any", preferences));
    }

    q = query(q, orderBy("posting_date", "desc"), limit(JOBS_PER_PAGE));

    if (startAfterDoc) {
      q = query(q, startAfter(startAfterDoc));
    }
    return q;
  }, [debouncedTitle, debouncedCompany, preferences]);

  const executeFetch = useCallback(async (isLoadMore = false) => {
     if (loading) return;
     setLoading(true);
     setError(null);

     try {
         // Determine if we are loading more or starting fresh
         // Note: We use 'lastDoc' from state if isLoadMore is true, else null.
         // Wait, 'lastDoc' state might be stale inside callback if dependencies are not correct?
         // But we are passing it to buildQuery.
         // Actually, if isLoadMore is true, we need the *current* lastDoc.
         // If isLoadMore is false, we start from scratch.

         const q = buildQuery(isLoadMore ? lastDoc : null);
         const querySnapshot = await getDocs(q);
         const fetchedJobs = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

         if (isLoadMore) {
             setJobs(prevJobs => [...prevJobs, ...fetchedJobs]);
         } else {
             setJobs(fetchedJobs);
         }

         const newLastDoc = querySnapshot.docs[querySnapshot.docs.length - 1];
         setLastDoc(newLastDoc);

         if (querySnapshot.docs.length < JOBS_PER_PAGE) {
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
  }, [buildQuery, lastDoc, loading]);


  // Effect for initial load and filter changes
  useEffect(() => {
    // Reset state and fetch
    setJobs([]);
    setLastDoc(null);
    setHasMore(true);

    // We can't reuse executeFetch here easily because it depends on state that we just reset (but React updates are async).
    // So we manually execute the first fetch logic here.

    const initialFetch = async () => {
        setLoading(true);
        setError(null);
        try {
            const q = buildQuery(null);
            const querySnapshot = await getDocs(q);
            const fetchedJobs = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

            setJobs(fetchedJobs);
            setLastDoc(querySnapshot.docs[querySnapshot.docs.length - 1]);

            if (querySnapshot.docs.length < JOBS_PER_PAGE) {
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
    // We add resetKey as dependency to force re-fetch when requested (e.g. Clear button)
  }, [buildQuery, resetKey]);

  const handleLoadMore = () => {
    executeFetch(true);
  };

  const handleClearSimilar = () => {
      setSimilarJobsTitle('');
      setResetKey(prev => prev + 1); // Trigger re-fetch of default list
  };

  const handleHide = useCallback(async (jobId) => {
    const user = auth.currentUser;
    if (!user) return;

    try {
      const userJobInteractionRef = doc(db, "users", user.uid, "job_interactions", jobId);
      await setDoc(userJobInteractionRef, { hidden: true }, { merge: true });
      setJobs(jobs.filter((job) => job.id !== jobId));
    } catch (err) {
      console.error("Error hiding job:", err);
      setError(err);
    }
  }, [jobs]);

  const handleHideCompany = useCallback(async (companyName) => {
    const user = auth.currentUser;
    if (!user) return;

    try {
      const hiddenCompanyRef = doc(db, "users", user.uid, "hidden_companies", companyName);
      await setDoc(hiddenCompanyRef, { name: companyName });
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
      const userJobInteractionRef = doc(db, "users", user.uid, "job_interactions", jobId);
      await setDoc(userJobInteractionRef, { pinned: !isPinned }, { merge: true });
      setJobs(prevJobs => prevJobs.map(job =>
          job.id === jobId ? { ...job, is_pinned: !isPinned } : job
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
      await api.post('/jobs/find-similar/', { link: job.link });
       alert("Similarity search initiated. Check back later.");
    } catch (err) {
      console.error("Error finding similar jobs:", err);
      setError(err);
    } finally {
      setIsLoadingSimilar(false);
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
                key={job.id} // Use job.id from Firestore
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
