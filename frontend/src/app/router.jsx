import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './appLayout';
import ProtectedRoute from '../ProtectedRoute';
import LoginPage from '../components/pages/LoginPage';
import DashboardPage from '../components/pages/DashboardPage';
import PropertiesPage from '../components/pages/PropertiesPage';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="properties" element={<PropertiesPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}