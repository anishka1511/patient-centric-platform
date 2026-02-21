import { useState, useRef } from 'react';
import { parseCSVData } from '../services/csvParser';
import '../styles/CSVUpload.css';

export default function CSVUpload({ onDataImported }) {
  const [isDragging, setIsDragging] = useState(false);
  const [importStatus, setImportStatus] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!/\.csv$/i.test(file.name)) {
      setImportStatus({ type: 'error', message: '❌ Please upload a CSV file' });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const doctors = parseCSVData(String(e.target.result || ''));
        setImportStatus({ type: 'success', message: `✓ Imported ${doctors.length} doctors` });
        setTimeout(() => {
          onDataImported(doctors);
          setImportStatus(null);
          if (fileInputRef.current) fileInputRef.current.value = '';
        }, 1500);
      } catch (error) {
        setImportStatus({ type: 'error', message: '❌ Error parsing CSV file' });
      }
    };
    reader.readAsText(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files[0]) handleFileSelect(files[0]);
  };

  const handleInputChange = (e) => {
    if (e.target.files[0]) handleFileSelect(e.target.files[0]);
  };

  return (
    <div className="csv-upload-container">
      <div
        className={`csv-drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">📁</div>
        <h3>Import Doctor Data</h3>
        <p>Drag & drop your CSV file here or click to browse</p>
        <span className="upload-hint">CSV format: doctors_name, doctors_location, specialty...</span>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        style={{ display: 'none' }}
        onChange={handleInputChange}
      />

      {importStatus && (
        <div className={`import-status ${importStatus.type}`}>
          {importStatus.message}
        </div>
      )}
    </div>
  );
}
