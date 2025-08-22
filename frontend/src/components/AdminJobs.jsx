import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './AdminJobs.css';

const AdminJobs = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchJobs = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/jobs/');
            setJobs(response.data);
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
    }, []);

    const handleDelete = async (jobLink) => {
        if (window.confirm('Are you sure you want to delete this job posting?')) {
            try {
                await api.delete(`/admin/jobs/${encodeURIComponent(jobLink)}/`);
                fetchJobs(); // Refresh the list
            } catch (err) {
                setError(err);
            }
        }
    };

    const handleRescrape = async (jobLink) => {
        try {
            await api.post(`/admin/jobs/${encodeURIComponent(jobLink)}/rescrape/`);
            alert('Rescrape task started. The job details will be updated in the background.');
        } catch (err) {
            setError(err);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div className="admin-jobs-container">
            <h1>Admin - Job Postings</h1>
            <table className="admin-jobs-table">
                <thead>
                    <tr>
                        <th>Job Title</th>
                        <th>Company</th>
                        <th>Location</th>
                        <th>Remote</th>
                        <th>Hybrid</th>
                        <th>Onsite</th>
                        <th>Updated</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {jobs.map(job => (
                        <tr key={job.link}>
                            <td><a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a></td>
                            <td>{job.company}</td>
                            <td>{job.location_string}</td>
                            <td>{job.remote ? 'Yes' : 'No'}</td>
                            <td>{job.hybrid ? 'Yes' : 'No'}</td>
                            <td>{job.onsite ? 'Yes' : 'No'}</td>
                            <td>{job.details_updated_at ? new Date(job.details_updated_at).toLocaleString() : 'Never'}</td>
                            <td>
                                <button onClick={() => handleRescrape(job.link)}>Rescrape</button>
                                <button onClick={() => handleDelete(job.link)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AdminJobs;
