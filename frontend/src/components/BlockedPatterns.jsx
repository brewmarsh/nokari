import React, { useState, useEffect } from "react";
import "./AdminJobs.css";
import api from '../services/api';

function BlockedPatterns() {
  const [patterns, setPatterns] = useState([]);
  const [newPattern, setNewPattern] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      const response = await api.get("/admin/blocked-patterns/");
      setPatterns(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleAddPattern = async (e) => {
    e.preventDefault();
    if (!newPattern.trim()) return;

    try {
      await api.post("/admin/blocked-patterns/", { pattern: newPattern });
      setNewPattern("");
      fetchPatterns();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeletePattern = async (id) => {
    try {
      await api.delete(`/admin/blocked-patterns/${id}/`);
      fetchPatterns();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading blocked patterns...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="admin-section">
      <h3>Blocked URL Patterns</h3>
      <p>
        URLs matching these patterns will be skipped during scraping. Supports wildcards (*).
        Example: https://example.com/blog/*
      </p>

      <form onSubmit={handleAddPattern} className="add-domain-form">
        <input
          type="text"
          value={newPattern}
          onChange={(e) => setNewPattern(e.target.value)}
          placeholder="Enter URL pattern to block"
          required
        />
        <button type="submit">Add Pattern</button>
      </form>

      <ul className="domain-list">
        {patterns.map((p) => (
          <li key={p.id} className="domain-item">
            {p.pattern}
            <button
              onClick={() => handleDeletePattern(p.id)}
              className="delete-btn"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BlockedPatterns;
