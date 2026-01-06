import React, { useState, useEffect } from 'react';
import Jobs from './Jobs.jsx';
import './Dashboard.css';
import { db } from '../firebaseConfig';
import { doc, updateDoc } from 'firebase/firestore';

const WorkArrangementFilter = ({ preferences, onPreferenceChange }) => {
    const options = ['remote', 'hybrid', 'onsite', 'unspecified'];

    const handleCheckboxChange = (option) => {
        const newPreferences = preferences.includes(option)
            ? preferences.filter(p => p !== option)
            : [...preferences, option];
        onPreferenceChange(newPreferences);
    };

    return (
        <div className="work-arrangement-filter">
            <h4>Work Arrangement</h4>
            {options.map(option => (
                <label key={option}>
                    <input
                        type="checkbox"
                        checked={preferences.includes(option)}
                        onChange={() => handleCheckboxChange(option)}
                    />
                    {option.charAt(0).toUpperCase() + option.slice(1)}
                </label>
            ))}
        </div>
    );
};

const Dashboard = ({ user }) => {
    const [preferences, setPreferences] = useState(user.preferred_work_arrangement || []);

    useEffect(() => {
        setPreferences(user.preferred_work_arrangement || []);
    }, [user.preferred_work_arrangement]);

    const handlePreferenceChange = async (newPreferences) => {
        setPreferences(newPreferences);
        try {
            const userDocRef = doc(db, "users", user.uid);
            await updateDoc(userDocRef, { preferred_work_arrangement: newPreferences });
        } catch (err) {
            console.error("Failed to save preferences:", err);
        }
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>Dashboard</h1>
            </div>
            <WorkArrangementFilter
                preferences={preferences}
                onPreferenceChange={handlePreferenceChange}
            />
            <Jobs preferences={preferences} user={user} />
        </div>
    );
};

export default Dashboard;
