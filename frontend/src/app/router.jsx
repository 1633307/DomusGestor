import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './appLayout';
import ProtectedRoute from '../components/layout/protectedRoute';
import LoginPage from '../features/auth/pages/loginPage';
import DashboardPage from '../features/dashboard/pages/dashboardPage';
import PropertiesPage from '../features/properties/pages/propertiesPage';

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