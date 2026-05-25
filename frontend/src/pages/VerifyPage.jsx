import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { validateData, downloadValidatedExcel, downloadGoodRecords, downloadRejectedRecords, getExcelUpload, checkJobStatus } from '../services/api';
import './VerifyPage.css';

function VerifyPage() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [isValidating, setIsValidating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    if (fileId) {
      loadFileDetails();
      runValidation();
    }
    
    // Cleanup on unmount
    return () => {
      if (window.wsConnection) {
        window.wsConnection.close();
      }
      if (window.wsPingInterval) {
        clearInterval(window.wsPingInterval);
      }
      if (window.fallbackPollInterval) {
        clearInterval(window.fallbackPollInterval);
      }
    };
  }, [fileId]);

  const loadFileDetails = async () => {
    try {
      const data = await getExcelUpload(fileId);
      setFileName(data.original_filename);
    } catch (err) {
      console.error('Error loading file details:', err);
    }
  };

  const runValidation = async () => {
    setIsValidating(true);
    setError(null);

    try {
      // Start validation - returns 202 with job_id
      const result = await validateData(fileId);
      
      if (result.job_id) {
        // Async job - connect to WebSocket for real-time updates
        setJobId(result.job_id);
        connectWebSocket(result.job_id);
      } else {
        // Old sync response (shouldn't happen)
        setValidationResult(result);
        setIsValidating(false);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error validating data');
      setIsValidating(false);
    }
  };

  const connectWebSocket = (jobId) => {
    // Close existing connection if any
    if (window.wsConnection) {
      window.wsConnection.close();
    }
    if (window.wsPingInterval) {
      clearInterval(window.wsPingInterval);
    }
    if (window.fallbackPollInterval) {
      clearInterval(window.fallbackPollInterval);
    }

    // Connect to WebSocket
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//localhost:8000/ws/job/${jobId}/`;
    
    const ws = new WebSocket(wsUrl);
    window.wsConnection = ws;
    
    let messageReceived = false;
    let connectionTimeout = null;

    // Fallback to HTTP polling if no messages received within 10 seconds
    connectionTimeout = setTimeout(() => {
      if (!messageReceived && ws.readyState === WebSocket.OPEN) {
        console.warn('No WebSocket messages received, falling back to HTTP polling');
        ws.close();
        startHttpPolling(jobId);
      }
    }, 10000);

    ws.onopen = () => {
      console.log('WebSocket connected for job:', jobId);
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        
        // Mark that we received a message
        if (data.type !== 'connection_established') {
          messageReceived = true;
          if (connectionTimeout) {
            clearTimeout(connectionTimeout);
            connectionTimeout = null;
          }
        }

        switch (data.type) {
          case 'connection_established':
            console.log('Connection confirmed:', data.message);
            break;

          case 'progress_update':
            setJobStatus(data);
            // Only update progress if it's higher than current (prevent regression)
            setProgress(prev => Math.max(prev, data.progress || 0));
            setCurrentStep(data.current_step || '');
            break;

          case 'job_completed':
            setJobStatus(data);
            setProgress(100);
            setCurrentStep('Processing complete');
            setValidationResult({
              validation_summary: {
                total_rows: data.total_rows,
                valid_rows: data.valid_rows,
                invalid_rows: data.invalid_rows,
                error_count: data.error_count,
              },
              status_message: data.status_message || 'Validation completed successfully',
              files_available: {
                all_records: true,
                good_records: data.valid_rows > 0,
                rejected_records: data.invalid_rows > 0,
              },
            });
            setIsValidating(false);
            ws.close();
            break;

          case 'job_failed':
            setError(data.error_message || 'Validation failed');
            setIsValidating(false);
            ws.close();
            break;

          case 'pong':
            // Pong response from ping
            break;

          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      console.log('Falling back to HTTP polling due to WebSocket error');
      if (connectionTimeout) clearTimeout(connectionTimeout);
      startHttpPolling(jobId);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      setWsConnected(false);
      if (connectionTimeout) clearTimeout(connectionTimeout);
      if (window.wsPingInterval) clearInterval(window.wsPingInterval);
      
      // If closed unexpectedly (not by completion), fall back to polling
      if (isValidating && !validationResult && !messageReceived) {
        console.log('WebSocket closed without receiving messages, falling back to HTTP polling');
        startHttpPolling(jobId);
      }
    };

    // Send periodic ping to keep connection alive
    window.wsPingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      } else {
        clearInterval(window.wsPingInterval);
      }
    }, 30000); // Ping every 30 seconds
  };

  const startHttpPolling = (jobId) => {
    console.log('Starting HTTP polling for job:', jobId);
    setCurrentStep('Checking status...');
    
    const pollStatus = async () => {
      try {
        const status = await checkJobStatus(jobId);
        
        if (status.status === 'completed') {
          setProgress(100);
          setCurrentStep('Processing complete');
          setValidationResult({
            validation_summary: {
              total_rows: status.total_rows,
              valid_rows: status.valid_rows,
              invalid_rows: status.invalid_rows,
              error_count: status.error_count,
            },
            status_message: status.status_message || 'Validation completed successfully',
            files_available: {
              all_records: true,
              good_records: status.valid_rows > 0,
              rejected_records: status.invalid_rows > 0,
            },
          });
          setIsValidating(false);
          if (window.fallbackPollInterval) {
            clearInterval(window.fallbackPollInterval);
          }
        } else if (status.status === 'failed') {
          setError(status.error_message || 'Validation failed');
          setIsValidating(false);
          if (window.fallbackPollInterval) {
            clearInterval(window.fallbackPollInterval);
          }
        } else {
          // Update progress (only if higher than current)
          setProgress(prev => Math.max(prev, status.progress || 0));
          setCurrentStep(status.current_step || 'Processing...');
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        setError('Error checking validation status');
        setIsValidating(false);
        if (window.fallbackPollInterval) {
          clearInterval(window.fallbackPollInterval);
        }
      }
    };
    
    // Poll immediately
    pollStatus();
    
    // Then poll every 2 seconds
    window.fallbackPollInterval = setInterval(pollStatus, 2000);
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);

    try {
      const blob = await downloadValidatedExcel(fileId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `verified_${fileName}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.error || 'Error downloading file');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDownloadGood = async () => {
    setIsDownloading(true);
    setError(null);

    try {
      const blob = await downloadGoodRecords(fileId);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `good_records_${fileName}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.error || 'Error downloading good records');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDownloadRejected = async () => {
    setIsDownloading(true);
    setError(null);

    try {
      const blob = await downloadRejectedRecords(fileId);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `rejected_records_${fileName}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.error || 'Error downloading rejected records');
    } finally {
      setIsDownloading(false);
    }
  };

  if (!fileId) {
    return (
      <div className="verify-page">
        <div className="card">
          <div className="alert alert-error">
            No file ID provided. Please upload a file first.
          </div>
          <Link to="/upload" className="btn btn-primary">
            Go to Upload Page
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-page">
      <div className="card page-card">
        <div className="page-header">
          <div>
            <h2>Step 3: Data Validation Complete</h2>
            {fileName && <p className="file-name">📄 {fileName}</p>}
          </div>
          <Link to="/upload" className="btn btn-secondary">
            ← Upload New File
          </Link>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {isValidating ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>{currentStep || 'Validating data... Please wait'}</p>
            {progress > 0 && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
                <p className="progress-text">{progress}%</p>
              </div>
            )}
            {jobId && (
              <p className="job-id-text">Job ID: {jobId}</p>
            )}
          </div>
        ) : (
          <>
            {validationResult && (
              <>
                <div className="summary-cards">
                  <div className="summary-card card-total">
                    <div className="card-icon">📊</div>
                    <div className="card-content">
                      <h3>{validationResult.validation_summary?.total_rows || 0}</h3>
                      <p>Total Rows</p>
                    </div>
                  </div>

                  <div className="summary-card card-valid">
                    <div className="card-icon">✅</div>
                    <div className="card-content">
                      <h3>{validationResult.validation_summary?.valid_rows || 0}</h3>
                      <p>Valid Rows</p>
                    </div>
                  </div>

                  <div className="summary-card card-invalid">
                    <div className="card-icon">❌</div>
                    <div className="card-content">
                      <h3>{validationResult.validation_summary?.invalid_rows || 0}</h3>
                      <p>Invalid Rows</p>
                    </div>
                  </div>

                  <div className="summary-card card-errors">
                    <div className="card-icon">🚨</div>
                    <div className="card-content">
                      <h3>{validationResult.validation_summary?.error_count || 0}</h3>
                      <p>Errors Found</p>
                    </div>
                  </div>
                </div>

                <div className="validation-message">
                  <h3>✓ Validation Complete</h3>
                  <p>
                    <strong>Status:</strong> {validationResult.status_message || 'Unknown'}
                  </p>
                  <p>Your data has been validated and split into separate files. Download the files below:</p>
                </div>

                <div className="action-buttons">
                  <button
                    className="btn btn-primary btn-large"
                    onClick={handleDownload}
                    disabled={isDownloading}
                  >
                    {isDownloading ? 'Downloading...' : '📥 Download All Records (With Errors)'}
                  </button>
                  
                  <button
                    className="btn btn-success btn-large"
                    onClick={handleDownloadGood}
                    disabled={isDownloading}
                  >
                    {isDownloading ? 'Downloading...' : '✅ Download Good Records Only'}
                  </button>
                  
                  <button
                    className="btn btn-danger btn-large"
                    onClick={handleDownloadRejected}
                    disabled={isDownloading}
                  >
                    {isDownloading ? 'Downloading...' : '❌ Download Rejected Records Only'}
                  </button>
                </div>

                <div className="download-info">
                  <p>
                    <strong>The downloaded Excel file contains:</strong>
                  </p>
                  <ul>
                    <li>✅ All your data with mapped headers</li>
                    <li>📋 A "Validation Errors" column showing all errors for each row (comma-separated)</li>
                    <li>🎨 Color-coded rows (red for rows with errors)</li>
                  </ul>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default VerifyPage;
