import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './appLayout';
import AppLayoutSideBar from './appLayoutSideBar';
import ProtectedRoute from '../ProtectedRoute';
import LoginPage from '../components/pages/LoginPage';
import DashboardPage from '../components/pages/DashboardPage';
import CercadorPage from '../components/pages/Cercador';
import InmoblesPage from '../components/pages/InmoblesPage';
import InfoInmoble from '../components/pages/InfoInmoble';


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
        <Route path="properties" element={<CercadorPage />} />
        <Route path="inmobles" element={<InmoblesPage />} />
             
      </Route>

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayoutSideBar />
          </ProtectedRoute>
        }
      >
      <Route path="infoInmoble" element={<InfoInmoble />} /> 
             
      </Route>

        
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}