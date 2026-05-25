import React from 'react';
import './DataPreview.css';

function DataPreview({ data, title = 'Data Preview' }) {
  if (!data || data.length === 0) {
    return (
      <div className="data-preview">
        <h3>{title}</h3>
        <p className="no-data">No data to preview</p>
      </div>
    );
  }

  const headers = Object.keys(data[0]);

  return (
    <div className="data-preview">
      <h3>{title}</h3>
      <p className="preview-info">Showing first {data.length} rows</p>
      
      <div className="preview-table-container">
        <table className="data-table preview-table">
          <thead>
            <tr>
              <th>#</th>
              {headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td className="row-number">{rowIndex + 1}</td>
                {headers.map((header, colIndex) => (
                  <td key={colIndex}>
                    {row[header] !== null && row[header] !== undefined 
                      ? String(row[header]) 
                      : <span className="empty-cell">-</span>
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataPreview;
