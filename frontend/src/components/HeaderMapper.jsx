import React, { useState, useEffect } from 'react';
import { getRegexPatterns } from '../services/api';
import './HeaderMapper.css';

function HeaderMapper({ headers, onMappingsChange, templates }) {
  const [mappings, setMappings] = useState({});
  const [validationRules, setValidationRules] = useState({});
  const [validationOptions, setValidationOptions] = useState({
    check_duplicates: true,
    check_empty_values: true,
    protect_good_records: false,
    hash_fields: []
  });
  const [regexPatterns, setRegexPatterns] = useState({});
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [showSaveTemplate, setShowSaveTemplate] = useState(false);
  const [templateName, setTemplateName] = useState('');

  useEffect(() => {
    // Fetch available regex patterns
    loadRegexPatterns();
    
    // Initialize mappings with original headers
    const initialMappings = {};
    const initialRules = {};
    headers.forEach(header => {
      initialMappings[header.original] = header.original;
      initialRules[header.original] = 'none'; // Default to no validation
    });
    setMappings(initialMappings);
    setValidationRules(initialRules);
    onMappingsChange(initialMappings, initialRules, validationOptions);
  }, [headers]);

  const loadRegexPatterns = async () => {
    try {
      const patterns = await getRegexPatterns();
      setRegexPatterns(patterns);
    } catch (err) {
      console.error('Error loading regex patterns:', err);
    }
  };

  const handleMappingChange = (original, newValue) => {
    const updatedMappings = {
      ...mappings,
      [original]: newValue,
    };
    setMappings(updatedMappings);
    onMappingsChange(updatedMappings, validationRules, validationOptions);
  };

  const handleValidationRuleChange = (original, ruleKey) => {
    const updatedRules = {
      ...validationRules,
      [original]: ruleKey,
    };
    setValidationRules(updatedRules);
    onMappingsChange(mappings, updatedRules, validationOptions);
  };

  const handleValidationOptionChange = (optionKey) => {
    const updatedOptions = {
      ...validationOptions,
      [optionKey]: !validationOptions[optionKey]
    };
    setValidationOptions(updatedOptions);
    onMappingsChange(mappings, validationRules, updatedOptions);
  };

  const handleHashFieldToggle = (fieldName) => {
    const currentHashFields = validationOptions.hash_fields || [];
    let updatedHashFields;
    
    if (currentHashFields.includes(fieldName)) {
      // Remove from hash fields
      updatedHashFields = currentHashFields.filter(f => f !== fieldName);
    } else {
      // Add to hash fields
      updatedHashFields = [...currentHashFields, fieldName];
    }
    
    const updatedOptions = {
      ...validationOptions,
      hash_fields: updatedHashFields
    };
    setValidationOptions(updatedOptions);
    onMappingsChange(mappings, validationRules, updatedOptions);
  };

  const handleTemplateSelect = (e) => {
    const templateId = e.target.value;
    setSelectedTemplate(templateId);

    if (templateId && templates) {
      const template = templates.find(t => t.id === parseInt(templateId));
      if (template && template.mapped_headers) {
        // Apply template mappings
        const updatedMappings = { ...mappings };
        Object.keys(template.mapped_headers).forEach(originalHeader => {
          if (updatedMappings.hasOwnProperty(originalHeader)) {
            updatedMappings[originalHeader] = template.mapped_headers[originalHeader];
          }
        });
        setMappings(updatedMappings);
        onMappingsChange(updatedMappings);
      }
    }
  };

  const handleSaveTemplate = () => {
    if (templateName.trim()) {
      // Emit save template event (handled by parent)
      onMappingsChange(mappings, validationRules, validationOptions, { saveTemplate: true, templateName });
      setShowSaveTemplate(false);
      setTemplateName('');
    }
  };

  return (
    <div className="header-mapper">
      {/* Validation Options Checkboxes */}
      <div className="validation-options">
        <h3>Validation Options</h3>
        <div className="options-grid">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={validationOptions.check_duplicates}
              onChange={() => handleValidationOptionChange('check_duplicates')}
            />
            <span>Check for Duplicates</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={validationOptions.check_empty_values}
              onChange={() => handleValidationOptionChange('check_empty_values')}
            />
            <span>Check for Empty Values</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={validationOptions.protect_good_records}
              onChange={() => handleValidationOptionChange('protect_good_records')}
            />
            <span>🔒 Protect Good Records (Lock cells from editing)</span>
          </label>
        </div>
      </div>

      {/* Hash Fields Selection */}
      <div className="validation-options">
        <h3>🔐 Hash Fields (SHA256) - Select fields to hash in good records:</h3>
        <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
          Selected fields will be hashed using SHA256 for security. Useful for mobile numbers, emails, etc.
        </p>
        <div className="options-grid">
          {Object.keys(mappings).map((originalHeader) => (
            <label key={originalHeader} className="checkbox-label">
              <input
                type="checkbox"
                checked={(validationOptions.hash_fields || []).includes(mappings[originalHeader])}
                onChange={() => handleHashFieldToggle(mappings[originalHeader])}
              />
              <span>{mappings[originalHeader]}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mapper-controls">
        <div className="control-group">
          <label htmlFor="template-select">Load Template:</label>
          <select
            id="template-select"
            value={selectedTemplate}
            onChange={handleTemplateSelect}
            className="template-select"
          >
            <option value="">-- Select a template --</option>
            {templates && templates.map(template => (
              <option key={template.id} value={template.id}>
                {template.template_name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setShowSaveTemplate(!showSaveTemplate)}
        >
          💾 Save as Template
        </button>
      </div>

      {showSaveTemplate && (
        <div className="save-template-form">
          <input
            type="text"
            className="input-field"
            placeholder="Enter template name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-success"
            onClick={handleSaveTemplate}
          >
            Save
          </button>
          <button
            type="button"
            className="btn"
            onClick={() => setShowSaveTemplate(false)}
          >
            Cancel
          </button>
        </div>
      )}

      <div className="mapping-table-container">
        <table className="data-table mapping-table">
          <thead>
            <tr>
              <th>Original Header</th>
              <th>Data Type</th>
              <th>Mapped Header</th>
              <th>Validation Rule</th>
            </tr>
          </thead>
          <tbody>
            {headers.map((header, index) => (
              <tr key={index}>
                <td>
                  <strong>{header.original}</strong>
                </td>
                <td>
                  <span className={`badge badge-${header.dataType}`}>
                    {header.dataType}
                  </span>
                </td>
                <td>
                  <input
                    type="text"
                    className="input-field mapping-input"
                    value={mappings[header.original] || ''}
                    onChange={(e) => handleMappingChange(header.original, e.target.value)}
                    placeholder="Enter new header name"
                  />
                </td>
                <td>
                  <select
                    className="input-field validation-select"
                    value={validationRules[header.original] || 'none'}
                    onChange={(e) => handleValidationRuleChange(header.original, e.target.value)}
                  >
                    {Object.entries(regexPatterns).map(([key, pattern]) => (
                      <option key={key} value={key} title={pattern.example}>
                        {pattern.description}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HeaderMapper;
