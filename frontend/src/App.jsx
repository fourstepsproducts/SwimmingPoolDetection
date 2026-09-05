import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnalysisProvider } from './context/AnalysisContext';
import MainLayout from './layouts/MainLayout';
import Monitoring from './pages/Monitoring';
import TestUpload from './pages/TestUpload';
import PoolMarkings from './pages/PoolMarkings';

function App() {
  return (
    <AnalysisProvider>
      <BrowserRouter>
        <Routes>
          {/* Dashboard Console Shell */}
          <Route element={<MainLayout />}>
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/test" element={<TestUpload />} />
            <Route path="/markings" element={<PoolMarkings />} />
            <Route path="/" element={<Navigate to="/monitoring" replace />} />
          </Route>

          {/* Catch-all Redirect */}
          <Route path="*" element={<Navigate to="/monitoring" replace />} />
        </Routes>
      </BrowserRouter>
      {/* Toast Alert Renderer */}
      <Toaster 
        position="top-right" 
        toastOptions={{
          className: 'font-sans text-xs',
          duration: 4000,
        }}
      />
    </AnalysisProvider>
  );
}

export default App;
