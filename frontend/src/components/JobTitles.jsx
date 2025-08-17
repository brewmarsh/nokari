import React, { useState, useEffect } from 'react';
import api from '../services/api';

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
        try {
            await api.delete(`/admin/job-titles/${id}/`);
            fetchJobTitles();
        } catch (err) {
            setError(err);
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
                    <li key={t.id}>
                        {t.title}
                        <button onClick={() => handleDelete(t.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default JobTitles;
