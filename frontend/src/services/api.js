import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session cookies
});

// Excel Upload API
export const uploadExcel = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/excel-uploads/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Get Available Regex Patterns API
export const getRegexPatterns = async () => {
  const response = await api.get('/excel-uploads/regex_patterns/');
  return response.data;
};

// Map Headers API
export const mapHeaders = async (fileId, mappings, validationRules = {}, validationOptions = {}) => {
  const response = await api.post(`/excel-uploads/${fileId}/map_headers/`, {
    mappings,
    validation_rules: validationRules,
    validation_options: validationOptions,
  });
  
  return response.data;
};

// Validate Data API
export const validateData = async (fileId) => {
  const response = await api.post(`/excel-uploads/${fileId}/validate/`);
  return response.data;
};

// Download Validated Excel API
export const downloadValidatedExcel = async (fileId) => {
  const response = await api.get(`/excel-uploads/${fileId}/download/`, {
    responseType: 'blob',
  });
  
  return response.data;
};

// Download Good Records Only API
export const downloadGoodRecords = async (fileId) => {
  const response = await api.get(`/excel-uploads/${fileId}/download_good_records/`, {
    responseType: 'blob',
  });
  
  return response.data;
};

// Download Rejected Records Only API
export const downloadRejectedRecords = async (fileId) => {
  const response = await api.get(`/excel-uploads/${fileId}/download_rejected_records/`, {
    responseType: 'blob',
  });
  
  return response.data;
};

// Get Mapping Templates API
export const getMappingTemplates = async () => {
  const response = await api.get('/mapping-templates/');
  return response.data;
};

// Save Mapping Template API
export const saveMappingTemplate = async (templateData) => {
  const response = await api.post('/mapping-templates/save_template/', templateData);
  return response.data;
};

// Get Excel Upload Details
export const getExcelUpload = async (fileId) => {
  const response = await api.get(`/excel-uploads/${fileId}/`);
  return response.data;
};

// Check Job Status API
export const checkJobStatus = async (jobId) => {
  const response = await api.get(`/queue-jobs/${jobId}/status/`);
  return response.data;
};

// Get Job Logs API
export const getJobLogs = async (jobId) => {
  const response = await api.get(`/queue-jobs/${jobId}/logs/`);
  return response.data;
};

export default api;
