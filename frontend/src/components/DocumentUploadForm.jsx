import React, { useState } from 'react';
import { auth, db, storage } from '../firebaseConfig';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

const DocumentUploadForm = ({ documentType, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !name) {
      setError("Please select a file and enter a name.");
      return;
    }

    const user = auth.currentUser;
    if (!user) {
      setError("User not authenticated.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const storageRef = ref(storage, `${documentType}s/${user.uid}/${file.name}`);
      const snapshot = await uploadBytes(storageRef, file);
      const downloadURL = await getDownloadURL(snapshot.ref);

      await addDoc(collection(db, "users", user.uid, `${documentType}s`), {
        name: name,
        file_url: downloadURL,
        uploaded_at: serverTimestamp(),
      });

      setFile(null);
      setName('');
      onUploadSuccess();
    } catch (err) {
      console.error(`Error uploading ${documentType}:`, err);
      setError(`Failed to upload ${documentType}: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input type="text" value={name} onChange={handleNameChange} placeholder={`Enter ${documentType} name`} required />
      <input type="file" onChange={handleFileChange} required />
      <button type="submit" disabled={uploading}>
        {uploading ? `Uploading ${documentType}...` : `Upload ${documentType}`}
      </button>
    </form>
  );
};

export default DocumentUploadForm;
