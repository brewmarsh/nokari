import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { db } from '../firebaseConfig';
import { doc, updateDoc } from 'firebase/firestore';

const Settings = ({ user }) => {
    const [preferences, setPreferences] = useState(user?.preferred_work_arrangement || []);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user) {
             setPreferences(user.preferred_work_arrangement || []);
        }
    }, [user]);

    const handleCheckboxChange = (option) => {
        setPreferences(prev => {
            if (prev.includes(option)) {
                return prev.filter(p => p !== option);
            } else {
                return [...prev, option];
            }
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSuccessMessage('');
        setError(null);
        setLoading(true);

        try {
            // Update Firestore (Source of Truth for Frontend)
            const userDocRef = doc(db, "users", user.uid);
            await updateDoc(userDocRef, { preferred_work_arrangement: preferences });

            // Update Backend (Sync)
            try {
                await api.patch('/me/', { preferred_work_arrangement: preferences });
            } catch (backendErr) {
                console.warn("Failed to sync settings to backend:", backendErr);
                // We proceed as success since Firestore is updated
            }

            setSuccessMessage('Your settings have been saved.');
        } catch (err) {
            console.error("Error saving settings:", err);
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    const options = ['remote', 'hybrid', 'onsite', 'unspecified'];

    if (!user) {
        return <div>Loading user data...</div>;
    }

    return (
        <div className="settings-container">
            <h1>Settings</h1>
            <form onSubmit={handleSubmit}>
                <div className="settings-section">
                    <h2>Preferred Work Arrangement</h2>
                    <p>Select the types of jobs you are interested in:</p>
                    <div className="checkbox-group">
                        {options.map(option => (
                            <label key={option} style={{ display: 'block', margin: '5px 0' }}>
                                <input
                                    type="checkbox"
                                    checked={preferences.includes(option)}
                                    onChange={() => handleCheckboxChange(option)}
                                    style={{ marginRight: '10px' }}
                                />
                                {option.charAt(0).toUpperCase() + option.slice(1)}
                            </label>
                        ))}
                    </div>
                </div>

                {error && <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>Error: {error.message}</div>}
                {successMessage && <p className="success-message" style={{ color: 'green', marginTop: '10px' }}>{successMessage}</p>}

                <button type="submit" disabled={loading} style={{ marginTop: '20px' }}>
                    {loading ? 'Saving...' : 'Save Settings'}
                </button>
            </form>
        </div>
    );
};

export default Settings;
