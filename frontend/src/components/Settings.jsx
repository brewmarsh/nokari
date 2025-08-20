import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Settings = () => {
    const [user, setUser] = useState(null);
    const [preferredWorkArrangement, setPreferredWorkArrangement] = useState('');
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await api.get('/me/');
                setUser(res.data);
                setPreferredWorkArrangement(res.data.preferred_work_arrangement || 'any');
            } catch (err) {
                setError(err);
            }
        };
        fetchUser();
    }, []);

    const handleChange = (e) => {
        setPreferredWorkArrangement(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSuccessMessage('');
        setError(null);
        try {
            await api.patch('/me/', { preferred_work_arrangement: preferredWorkArrangement });
            setSuccessMessage('Your settings have been saved.');
        } catch (err) {
            setError(err);
        }
    };

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Settings</h1>
            <form onSubmit={handleSubmit}>
                <h2>Preferences</h2>
                <div>
                    <label htmlFor="work-arrangement" style={{ marginRight: '10px' }}>Preferred Work Arrangement</label>
                    <select id="work-arrangement" value={preferredWorkArrangement} onChange={handleChange}>
                        <option value="any">Any</option>
                        <option value="remote">Remote</option>
                        <option value="hybrid">Hybrid</option>
                        <option value="onsite">Onsite</option>
                    </select>
                </div>
                <button type="submit" style={{ marginTop: '20px' }}>Save Settings</button>
            </form>
            {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
        </div>
    );
};

export default Settings;
