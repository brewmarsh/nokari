import React, { useState, useEffect, useCallback } from 'react';
import DocumentUploadForm from './DocumentUploadForm.jsx';
import { db, auth } from '../firebaseConfig';
import { collection, query, where, getDocs } from 'firebase/firestore';

const Documents = () => {
  const [resumes, setResumes] = useState([]);
  const [coverLetters, setCoverLetters] = useState([]);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    const user = auth.currentUser;
    if (!user) {
      setError(new Error("User not authenticated."));
      return;
    }

    try {
      const resumesQuery = query(collection(db, "users", user.uid, "resumes"));
      const resumesSnapshot = await getDocs(resumesQuery);
      setResumes(resumesSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));

      const coverLettersQuery = query(collection(db, "users", user.uid, "cover_letters"));
      const coverLettersSnapshot = await getDocs(coverLettersQuery);
      setCoverLetters(coverLettersSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));

    } catch (err) {
      console.error("Error fetching documents:", err);
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
