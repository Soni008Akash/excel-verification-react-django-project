import React, { useState } from 'react';
import './ValidationReport.css';

function ValidationReport({ summary, errors, warnings }) {
  const [showErrors, setShowErrors] = useState(true);
  const [showWarnings, setShowWarnings] = useState(true);

  return (
    <div className="validation-report">
      <h2>Validation Report</h2>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card card-total">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <h3>{summary?.total_rows || 0}</h3>
            <p>Total Rows</p>
          </div>
        </div>

        <div className="summary-card card-valid">
          <div className="card-icon">✅</div>
          <div className="card-content">
            <h3>{summary?.valid_rows || 0}</h3>
            <p>Valid Rows</p>
          </div>
        </div>

        <div className="summary-card card-invalid">
          <div className="card-icon">❌</div>
          <div className="card-content">
            <h3>{summary?.invalid_rows || 0}</h3>
            <p>Invalid Rows</p>
          </div>
        </div>

        <div className="summary-card card-errors">
          <div className="card-icon">🚨</div>
          <div className="card-content">
            <h3>{summary?.error_count || 0}</h3>
            <p>Errors</p>
          </div>
        </div>

        <div className="summary-card card-warnings">
          <div className="card-icon">⚠️</div>
          <div className="card-content">
            <h3>{summary?.warning_count || 0}</h3>
            <p>Warnings</p>
          </div>
        </div>
      </div>

      {/* Errors Section */}
      {errors && errors.length > 0 && (
        <div className="report-section">
          <div className="section-header" onClick={() => setShowErrors(!showErrors)}>
            <h3>
              🚨 Errors ({errors.length})
            </h3>
            <button className="toggle-btn">
              {showErrors ? '▼' : '▶'}
            </button>
          </div>

          {showErrors && (
            <div className="errors-list">
              {errors.map((error, index) => (
                <div key={index} className="error-item">
                  <div className="error-header">
                    <span className="error-row">
                      Row {error.row || error.rows?.join(', ')}
                    </span>
                    <span className="error-column">{error.column}</span>
                  </div>
                  <p className="error-message">{error.issue}</p>
                  {error.value && (
                    <p className="error-value">
                      <strong>Value:</strong> {error.value}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Warnings Section */}
      {warnings && warnings.length > 0 && (
        <div className="report-section">
          <div className="section-header" onClick={() => setShowWarnings(!showWarnings)}>
            <h3>
              ⚠️ Warnings ({warnings.length})
            </h3>
            <button className="toggle-btn">
              {showWarnings ? '▼' : '▶'}
            </button>
          </div>

          {showWarnings && (
            <div className="warnings-list">
              {warnings.map((warning, index) => (
                <div key={index} className="warning-item">
                  <div className="warning-header">
                    <span className="warning-column">{warning.column}</span>
                  </div>
                  <p className="warning-message">{warning.issue}</p>
                  {warning.rows && (
                    <p className="warning-rows">
                      <strong>Affected Rows:</strong>{' '}
                      {warning.rows.slice(0, 10).join(', ')}
                      {warning.rows.length > 10 && '...'}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Success Message */}
      {(!errors || errors.length === 0) && (!warnings || warnings.length === 0) && (
        <div className="success-message">
          <div className="success-icon">🎉</div>
          <h3>Perfect! No issues found</h3>
          <p>All data passed validation successfully</p>
        </div>
      )}
    </div>
  );
}

export default ValidationReport;
