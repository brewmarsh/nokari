import React, { useState, useEffect, useCallback } from 'react';
import './Jobs.css';
import useDebounce from '../hooks/useDebounce.js';
import { db, auth } from '../firebaseConfig';
import { collection, query, where, getDocs, doc, updateDoc, deleteDoc, setDoc } from 'firebase/firestore';
import api from '../services/api'; // Keep api for find-similar for now

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
    setError(null); // Clear previous errors
    try {
      const jobsRef = collection(db, "job_postings");
      let q = query(jobsRef);

      if (debouncedTitle) {
        q = query(q, where("title", "==", debouncedTitle));
      }
      if (debouncedCompany) {
        q = query(q, where("company", "==", debouncedCompany));
      }
      // For 'search' and 'work_arrangement', Firestore has limitations for complex queries.
      // For now, we'll handle simple filtering. More complex search might require a dedicated search service.
      if (preferences && preferences.length > 0) {
        // Assuming 'locations' field in job_postings is an array and 'preferences' can match
        // This is a simplified approach. Real-world might need more complex logic.
        q = query(q, where("locations", "array-contains-any", preferences));
      }

      const querySnapshot = await getDocs(q);
      const fetchedJobs = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setJobs(fetchedJobs);
    } catch (err) {
      console.error("Error fetching jobs:", err);
      setError(err);
    }
  }, [debouncedTitle, debouncedCompany, debouncedSearch, preferences]);

  useEffect(() => {
    fetchJobs();
  }, [debouncedTitle, debouncedCompany, debouncedSearch, fetchJobs, preferences]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

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
      // Re-fetch jobs to update the pinned status in the UI
      fetchJobs();
    } catch (err) {
      console.error("Error pinning job:", err);
      setError(err);
    }
  }, [fetchJobs]);

  const handleFindSimilar = useCallback(async (job) => {
    setIsLoadingSimilar(true);
    setSimilarJobsTitle(job.title);
    setOpenMenu(null);
    try {
      // This still calls the backend API as similarity search is a backend operation
      const res = await api.post('/jobs/find-similar/', { link: job.link });
      // The response from backend should ideally trigger a Firestore update
      // or provide a task_id to poll Firestore for results.
      // For now, we'll assume the backend will handle populating Firestore
      // and we might need to fetch from Firestore based on task_id.
      // For simplicity, we'll just re-fetch all jobs for now.
      fetchJobs();
    } catch (err) {
      console.error("Error finding similar jobs:", err);
      setError(err);
    } finally {
      setIsLoadingSimilar(false);
    }
  }, [fetchJobs]);

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
        </>
      )}
    </div>
  );
};

export default Jobs;
