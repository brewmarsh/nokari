import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import DocumentUploadForm from './DocumentUploadForm.jsx';

const Documents = () => {
  const [resumes, setResumes] = useState([]);
  const [coverLetters, setCoverLetters] = useState([]);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const resumesRes = await api.get('/resumes/');
      setResumes(resumesRes.data);
      const coverLettersRes = await api.get('/cover-letters/');
      setCoverLetters(coverLettersRes.data);
    } catch (err) {
      setError(err);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUploadSuccess = useCallback(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>Document Management</h1>

      <h2>Resumes</h2>
      <ul>
        {resumes.map(resume => (
          <li key={resume.id}>{resume.name}</li>
        ))}
      </ul>
      <DocumentUploadForm documentType="resume" onUploadSuccess={handleUploadSuccess} />

      <h2>Cover Letters</h2>
      <ul>
        {coverLetters.map(coverLetter => (
          <li key={coverLetter.id}>{coverLetter.name}</li>
        ))}
      </ul>
      <DocumentUploadForm documentType="cover-letter" onUploadSuccess={handleUploadSuccess} />
    </div>
  );
};

export default Documents;
