import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './appLayout';
import AppLayoutSideBar from './appLayoutSideBar';
import ProtectedRoute from '../ProtectedRoute';
import LoginPage from '../components/pages/LoginPage';
import DashboardPage from '../components/pages/DashboardPage';
import CercadorPage from '../components/pages/CercadorPage';
import InmoblesPage from '../components/pages/InmoblesPage';
import InfoInmoble from '../components/pages/InfoInmoblePage';
import ReservesPage from '../components/pages/reservesPage';
import InfoReserva from '../components/pages/infoReservaPage';

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
        <Route path="reserves" element={<ReservesPage />} />
        <Route path="infoInmoble" element={<InfoInmoble />} />
        <Route path="infoReserva" element={<InfoReserva />} />  
             
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}