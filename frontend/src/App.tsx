import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { ClinicianDashboard } from './pages/ClinicianDashboard';
import { PatientPortal } from './pages/PatientPortal';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/clinician" element={<ClinicianDashboard />} />
        <Route path="/patient" element={<PatientPortal />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
