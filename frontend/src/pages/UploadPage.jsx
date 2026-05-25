import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import HeaderMapper from '../components/HeaderMapper';
import {
  uploadExcel,
  mapHeaders,
  getMappingTemplates,
  saveMappingTemplate,
} from '../services/api';
import './UploadPage.css';

function UploadPage() {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [headers, setHeaders] = useState([]);
  const [mappings, setMappings] = useState({});
  const [validationRules, setValidationRules] = useState({});
  const [validationOptions, setValidationOptions] = useState({
    check_duplicates: true,
    check_empty_values: true,
    protect_good_records: false,
    hash_fields: []
  });
  const [templates, setTemplates] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    // Load mapping templates on component mount
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await getMappingTemplates();
      setTemplates(data);
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await uploadExcel(file);
      setUploadedFile({
        id: response.file_id,
        name: response.filename,
        rowCount: response.row_count,
      });
      setHeaders(response.headers);
      setSuccess(`File uploaded successfully! Found ${response.row_count} rows.`);
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setIsUploading(false);
    }
  };

  const handleMappingsChange = async (newMappings, newValidationRules, newValidationOptions, options = {}) => {
    setMappings(newMappings);
    setValidationRules(newValidationRules || {});
    setValidationOptions(newValidationOptions || { check_duplicates: true, check_empty_values: true, protect_good_records: false, hash_fields: [] });

    // If save template is requested
    if (options.saveTemplate && options.templateName) {
      try {
        const originalHeaders = headers.map(h => h.original);
        await saveMappingTemplate({
          template_name: options.templateName,
          original_headers: originalHeaders,
          mapped_headers: newMappings,
        });
        setSuccess('Template saved successfully!');
        loadTemplates(); // Reload templates
      } catch (err) {
        setError(err.response?.data?.error || 'Error saving template');
      }
    }
  };

  const handleProceedToValidation = async () => {
    if (!uploadedFile || !mappings || Object.keys(mappings).length === 0) {
      setError('Please upload a file and map headers');
      return;
    }

    try {
      // Save header mappings, validation rules, and validation options to backend
      await mapHeaders(uploadedFile.id, mappings, validationRules, validationOptions);
      
      // Navigate to verify page
      navigate(`/verify/${uploadedFile.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Error saving mappings');
    }
  };

  return (
    <div className="upload-page">
      <div className="card page-card">
        <h2>Step 1: Upload Excel File</h2>
        <p className="page-description">
          Upload your Excel file (.xlsx, .xls, .csv) to begin the verification process.
        </p>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}

        <FileUploader onFileUpload={handleFileUpload} isLoading={isUploading} />

        {uploadedFile && (
          <div className="file-info">
            <h3>✅ File Uploaded</h3>
            <p><strong>Filename:</strong> {uploadedFile.name}</p>
            <p><strong>Total Rows:</strong> {uploadedFile.rowCount}</p>
          </div>
        )}

        {headers.length > 0 && (
          <>
            <div className="section-divider"></div>
            
            <h2>Step 2: Map Headers</h2>
            <p className="page-description">
              Review and rename the column headers as needed. You can save your mappings as a template for future use.
            </p>

            <HeaderMapper
              headers={headers}
              onMappingsChange={handleMappingsChange}
              templates={templates}
            />

            <div className="action-buttons">
              <button
                className="btn btn-primary btn-large"
                onClick={handleProceedToValidation}
              >
                Next: Verify Data →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default UploadPage;
