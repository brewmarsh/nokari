import React, { useState, useEffect } from 'react';
import api from '../services/api';

const TrashIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
    </svg>
  );

const JobTitles = () => {
    const [jobTitles, setJobTitles] = useState([]);
    const [error, setError] = useState(null);
    const [title, setTitle] = useState('');

    const fetchJobTitles = async () => {
        try {
            const res = await api.get('/admin/job-titles/');
            setJobTitles(res.data);
        } catch (err) {
            setError(err);
        }
    };

    useEffect(() => {
        fetchJobTitles();
    }, []);

    const onChange = (e) => setTitle(e.target.value);

    const onSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/job-titles/', { title });
            setTitle('');
            fetchJobTitles();
        } catch (err) {
            setError(err);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this job title?')) {
            try {
                await api.delete(`/admin/job-titles/${id}/`);
                fetchJobTitles();
            } catch (err) {
                setError(err);
            }
        }
    };

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div>
            <h1>Searchable Job Titles</h1>
            <form onSubmit={onSubmit}>
                <input
                    type="text"
                    placeholder="Enter a job title"
                    value={title}
                    onChange={onChange}
                    required
                />
                <button type="submit">Add Job Title</button>
            </form>
            <ul>
                {jobTitles.map((t) => (
                    <li key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        {t.title}
                        <button onClick={() => handleDelete(t.id)} style={{ color: 'red', background: 'none', border: 'none', cursor: 'pointer' }}>
                            <TrashIcon />
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default JobTitles;
