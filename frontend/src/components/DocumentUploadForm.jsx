import React, { useState } from 'react';
import api from '../services/api';

const DocumentUploadForm = ({ documentType, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    try {
      await api.post(`/${documentType}s/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess();
    } catch (error) {
      console.error(`Error uploading ${documentType}:`, error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={name} onChange={handleNameChange} placeholder={`Enter ${documentType} name`} required />
      <input type="file" onChange={handleFileChange} required />
      <button type="submit">Upload {documentType}</button>
    </form>
  );
};

export default DocumentUploadForm;
