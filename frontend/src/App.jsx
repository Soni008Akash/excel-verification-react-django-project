import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import VerifyPage from './pages/VerifyPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>📊 Excel Data Verification Tool</h1>
          <p>Upload, Map Headers, and Validate Your Excel Data</p>
        </header>
        
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/verify/:fileId" element={<VerifyPage />} />
          </Routes>
        </main>
        
        <footer className="app-footer">
          <p>&copy; 2026 Excel Verify Project. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
