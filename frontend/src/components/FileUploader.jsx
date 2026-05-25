import React, { useState, useRef } from 'react';
import './FileUploader.css';

function FileUploader({ onFileUpload, isLoading }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
      alert(`File type not supported. Please upload: ${allowedExtensions.join(', ')}`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10MB limit');
      return;
    }

    onFileUpload(file);
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-uploader">
      <form
        className={`upload-form ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onSubmit={(e) => e.preventDefault()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          accept=".xlsx,.xls,.csv"
          onChange={handleChange}
          disabled={isLoading}
        />

        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <p className="upload-text">
            {isLoading ? 'Uploading...' : 'Drag and drop your Excel file here'}
          </p>
          <p className="upload-subtext">or</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onButtonClick}
            disabled={isLoading}
          >
            Browse Files
          </button>
          <p className="upload-info">Supported formats: .xlsx, .xls, .csv (Max 10MB)</p>
        </div>
      </form>
    </div>
  );
}

export default FileUploader;
